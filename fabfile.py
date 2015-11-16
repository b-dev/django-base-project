#import os, time, random, getpass, sys
#from os.path import abspath, dirname, isfile
import os
import random
from fabric.api import *
from fabric.contrib.console import confirm
#from fabric.contrib.files import append, exists

PRJ_ROOT = os.path.dirname(os.path.abspath(__file__))
PRJ_NAME = os.path.basename(PRJ_ROOT)
from fabric.contrib.files import sed

ENVIRONMENTS = {
    'dev': ['localhost'],
    'staging': '',
    'production': '',
    'test': '',
}

env.user = 'django'
# to enable ssh key forwarding
env.forward_agent = True

@task
def dev():
    env.name = 'dev'
    env.hosts = ENVIRONMENTS[env.name]

@task
def staging():
    env.name = 'staging'
    env.hosts = ENVIRONMENTS[env.name]

@task
def production():
    env.name = 'production'
    env.hosts = ENVIRONMENTS[env.name]

@task
def test():
    env.name = 'test'
    env.hosts = ENVIRONMENTS[env.name]


@task
def bower():
    from sh import bower
    pah = os.path.join(PRJ_ROOT, 'requirements', 'front_base.txt')
    with open(pah, 'r') as reqfile:
        for line in reqfile:
            bower.install(line.strip())


########################
### PRODUCTION TASK ####
########################
@task
def project_setup():
    if not exists("/home/django/.virtualenvs/%s" % PRJ_NAME):
        run('mkvirtualenv %s' % (PRJ_NAME,))

    # Clono, se non e' gia stato clonato il progetto
    with cd("/home/django/"):
        if not exists(PRJ_NAME):
            run('git clone %s %s' % (PRJ_GIT_REPO, PRJ_NAME))

        with prefix('workon %s' % PRJ_NAME):
            # Aggiungo all'ambiente virtuale la directory base del progetto e la directory apps
            run("add2virtualenv /home/django/%s" % PRJ_NAME)
            run("add2virtualenv /home/django/%s/external_apps" % PRJ_NAME)
            run("add2virtualenv /home/django/%s/website" % PRJ_NAME)

            with cd(PRJ_NAME):
                # Installo i pacchetti necessari
                run("pip install -r requirements/%s.txt" % env.name)

    # Creo il db
    remote_db_name = raw_input(u"db name for the %s db ? (defaults to project name) \n" % env.name)
    if len(remote_db_name.strip()) == 0:
        remote_db_name = PRJ_NAME

    remote_db_user = raw_input(u"username for the %s db ? (defaults to db name) \n" % env.name)
    if len(remote_db_user.strip()) == 0:
        remote_db_user = remote_db_name

    remote_db_pass = getpass.getpass(u"password for the %s db ? (defaults to username) \n" % env.name)
    if len(remote_db_pass.strip()) == 0:
        remote_db_pass = remote_db_user

    run("createuser -U postgres -d -R -S %s" % remote_db_user)
    run("createdb -U %s -h localhost %s" % (remote_db_user, remote_db_name))

    with cd("/home/django/%s/" % PRJ_NAME):
        run("touch .env")
        append(".env", "PRJ_ENV=%s" % env.name)
        append(".env", "PRJ_DB_NAME=%s" % remote_db_name)
        append(".env", "PRJ_DB_USER=%s" % remote_db_user)
        append(".env", "PRJ_DB_PASSWORD=%s" % remote_db_pass)
        append(".env", 'PRJ_SECRET_KEY="%s"' % "".join([random.choice(
                             "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_+)") for i in range(50)]))

    # Installazione app e db
    with cd("/home/django/%s/website" % PRJ_NAME):
        with prefix('workon %s' % PRJ_NAME):
            run("python manage.py syncdb --all")
            run("python manage.py migrate --fake")
            run("python manage.py collectstatic")

    env.user = 'root'

    # Per sicurezza, rendo eseguibile il file conf/gunicorn.sh
    with cd("/home/django/%s/etc" % PRJ_NAME):
        run("chmod +x gunicorn.sh")

    with cd("/etc/nginx/sites-enabled/"):
        run("ln -s /home/django/%s/etc/nginx.conf %s" % (PRJ_NAME, PRJ_NAME))

    with cd("/etc/supervisor/conf.d/"):
        run("ln -s /home/django/%s/etc/supervisor.conf %s.conf" % (PRJ_NAME, PRJ_NAME))

    run("/etc/init.d/supervisor stop")
    time.sleep(5)
    run("/etc/init.d/supervisor start")
    run("supervisorctl reload")
    run("/etc/init.d/nginx reload")


@task
def update():
    # Clono, se non e' gia stato clonato il progetto
    with cd("/home/django/%s" % PRJ_NAME):
        run("git pull")
        with prefix('workon %s' % PRJ_NAME):
            run("pip install -r requirements.txt")
            run("python manage.py migrate")
            run("python manage.py collectstatic --noinput")
    env.user = 'root'
    run('supervisorctl reload')


@task
def reload_server():
    env.user = 'root'
    run('/etc/init.d/nginx reload')
    run('supervisorctl reload')


@task
def reload_supervisor():
    env.user = 'root'
    run('supervisorctl reload')


@task
def restart_server():
    env.user = 'root'
    run('/etc/init.d/nginx restart')
    run("/etc/init.d/supervisor stop")
    time.sleep(5)
    run("/etc/init.d/supervisor start")


########################
### DEVELOPMENT TASK ###
########################
def _replace_variable_in_files(prj_root, list_files, dv):
    print list_files
    for file_name in list_files:
        fpath = prj_root+"/"+file_name
        with open(fpath) as f:
            s = f.read()
        for key in dv.keys():
            s = s.replace(key, dv[key])
        with open(fpath, 'w') as f:
            f.write(s)

@task
def local_project_setup():
    enable_cms = 'False'
    deploy_on_heroku = 'False'

    if confirm("Do you want to enable the CMS (y/n)?", default=False):
        enable_cms = 'True'

    if confirm("Will you deploy the app on Heroku (y/n)?", default=False):
        deploy_on_heroku = 'True'

    db_name = prompt(u"PostreSQL DB name for the local db? (It will be created if doesn't exist)", validate=r'^\w+$')
    db_user = prompt(u"PostgreSQL username for the local db? (It will be created if doesn't exist)", validate=r'^\w+$')
    db_password = '1'
    db_password_check = '2'
    while db_password != db_password_check:
        db_password = prompt(u"PostgreSQL password for the local db ?")
        db_password_check = prompt(u"Rewrite password for the local db ?")
        if db_password != db_password_check:
            print "The passwords didn't match. Retry."

    git_repo = prompt(u"repo url for the project ? (can be left empty and configured in git later)")

    # generate two different secret key, one for dev and one for production
    dev_secret_key = ''.join(
        [random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
    prod_secret_key = ''.join(
        [random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])

    list_files_to_update = ['etc/gunicorn.sh', 'etc/nginx.conf', 'etc/supervisor.conf',
                            'website/settings/base.py', 'website/settings/dev.py', 'website/settings/production.py',]

    dict_var_to_update = {'%%PRJ_NAME%%': PRJ_NAME,
                          '%%PRJ_ENABLE_CMS%%': enable_cms,
                          '%%DEPLOY_ON_HEROKU%%': deploy_on_heroku,
                          '%%DB_NAME%%': db_name,
                          '%%DB_USER%%': db_user,
                          '%%DB_PASSWORD%%': db_password,
                          '%%GIT_REPO%%': git_repo,
                          '%%DEV_SECRET_KEY%%': dev_secret_key,
                          '%%PROD_SECRET_KEY%%': prod_secret_key
                          }
    _replace_variable_in_files(PRJ_ROOT, list_files_to_update, dict_var_to_update)

    local('rm -f .hgignore')
    local('rm -fr .hg')
    local('rm -fr .git')
    if git_repo:
        local('git init')
        local('git remote add origin %s' % (git_repo))
        local('git add .')

    with settings(hide('running', 'stdout', 'stderr', 'warnings'),
                  warn_only=True):
        res = local('''psql -U postgres -t -A -c "SELECT COUNT(*) FROM pg_user WHERE usename = '%s';"''' % db_user)
        # 1 = User exists
        if str(res) != "1":
            local('''psql -U postgres -c "CREATE USER %s CREATEDB CREATEROLE PASSWORD '%s';"''' % (db_user, db_password))

    with settings(hide('running', 'stdout', 'stderr', 'warnings'),
                  warn_only=True):
        db_exists = local('''psql -U postgres -d %s -c ""''' % db_name).succeeded
        if not db_exists:
            print "creating database %s ...." % db_name
            local('''createdb --owner %s --template template0 \
                --encoding=UTF8 --lc-ctype=en_US.UTF-8 \
                --lc-collate=en_US.UTF-8 %s''' % (db_user, db_name))
        else:
            print "Database %s already exists ...." % db_name

    local("pip install -r requirements/base.txt")
    if enable_cms == 'True':
        local("pip install -r requirements/cms.txt")
    if deploy_on_heroku == 'True':
        local("pip install -r requirements/heroku.txt")

    local("python manage.py syncdb --all")
    local("python manage.py migrate --fake")
