====================
D-light base project
====================

A complete skeleton for Django projects, using:
-----------------------------------------------
* Django 1.6
* Pip
* virtualenv and virtualenvwrapper
* Bower

Project also have a configuration to use Vagrant (1.2.2) on VirtualBox (4.2.12) during development, tested with PyCharm on Ubuntu and MacOSX.
Deployment is made with Gunicorn and Nginx.

==================================
Initial Server Setup
==================================

Follow these step to install all required package: ::


    apt-get -y update
    apt-get -y install nginx postgresql libpq-dev python-dev gcc make python-setuptools libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev mercurial subversion git supervisor

    # SE SI HANNO PROBLEMI CON PIL PERCHE NON INSTALLA IL SUPPORTO AL JPEG (TENDENZIALMENTE IL PROBLEMA SI HA CON LE VERSIONI A 64 BIT) CREARE I SEGUENTI LINK SIMBOLICI:
    # ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib
    # ln -s /usr/lib/x86_64-linux-gnu/libfreetype.so /usr/lib
    # ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib

    # Create postgres user 'django'
    su postgres -c "createuser -P django"

    ### VIRTUALENV ###
    easy_install elementtree
    easy_install pip
    pip install virtualenv
    pip install virtualenvwrapper

    ## CREATE DJANGO USER ##
    useradd -d /home/django -m -r django
    passwd django

    ## THIS STEP MUST BE DONE WITH django USER
    su - django

    # Open /home/django/.bashrc file and add this 3 lines at the bottom of the files:
    export WORKON_HOME=$HOME/.virtualenvs
    source /usr/local/bin/virtualenvwrapper.sh
    export DJANGO_ENVIRONMENT=production

    mkdir /home/django/.virtualenvs

    # open (or create if not exists) /home/django/.bash_profile and add these lines:
    if [ -f "$HOME/.bashrc" ]; then
        . "$HOME/.bashrc"
    fi
    export WORKON_HOME=$HOME/.virtualenvs
    source /usr/local/bin/virtualenvwrapper.sh
    export DJANGO_ENVIRONMENT=production


==================================
Local Development without Vagrant
==================================

To locally deploy this template into a new project, you need to follow these steps:
-----------------------------------------------------------------------------------

::

    git clone git@github.com:marcominutoli/b-light-base-project.git [project_name]

::

    cd [project_name]
    mkvirtualenv [project_name]
    make project_setup


Add external (included) apps to the project
-------------------------------------------

There are two 'pre-installed' apps inside the base project: the CMS apps and the WEBAPP apps.

* 'cms'    : install django-cms and the django filer utility.
* 'webapp' : installs redis server and django-rest-framework apps, so you can easly expose your api to the web.

There are disabled by default.
To enable these apps run the following command:

::

    fab plug:cms # to enable the CMS apps
    fab plug:webapp # to enable the WEBAPP apps

Now you can run "runserver" and browse yoour app :-)

==================================
Local Development with Vagrant
==================================

To locally deploy this template into a new project with Vagrant, you need to follow these steps:
------------------------------------------------------------------------------------------------

::

    git clone git@github.com:marcominutoli/b-light-base-project.git [project_name]

::

    cd [project_name]/bin
    python bootstrap.py [env_type]

env_type choices are:

 * 'dev' ( the usual stuff; embedded static files serving, debug toolbar, django extensions )
 * 'test' ( todo description )
 * 'staging' ( todo description )
 * 'production' ( todo description )

( note that currently VirtualBox 4.2.14 seems bugged and will fail when importing the vagrant box )::
::

    vagrant plugin install vagrant-vbguest  ( just the first time )
    cd ..
    vagrant up

This initialize a virtual machine with a user 'django' (password 'django') providing a virtualenv connected to the project.
Debian packages are kept upgraded by the provisioning as long PRJ_DEB_UPGRADE=TRUE in .env file.
The same for Pip packages in the virtualenv with PRJ_PIP_UPGRADE=TRUE.

The vagrant-vbguest plugin will keep VirtualBox Guest Additions up to date on the VM,
if the base vagrant image has already additions installed an error could be thrown, in that case you should vagrant ssh and :
::

    sudo apt-get remove virtualbox-guest-dkms virtualbox-guest-utils virtualbox-guest-x11
    sudo dpkg --purge virtualbox-guest-utils virtualbox-guest-x11
    sudo apt-get autoremove
    exit
    vagrant reload --provision


Deploy application on Heroku:
-----------------------------

Here, I describe quickly the steps to deploy your app on Heroku. If you want to read a complete guide, go to the official heroku site:

::

    https://devcenter.heroku.com/articles/getting-started-with-django

To deploy your application on heroku, first you have to install "Foreman" packages:

::

    gem install foreman

To test your application run (in you project root directory, where Procfile is located):

::

    formean start


Create the 'requirements.txt' file in you root directory:

::

    pip freeze > requirements.txt


Set to True the **DEPLOY_ON_HEROKU** settings in setting/base.py and then commit/push to the repository:

::

    DEPLOY_ON_HEROKU = True # in settings/base.py
    git push

The next step is to push the application’s repository to Heroku. First, we have to get a place to push to from Heroku. We can do this with the heroku create command:

::

    heroku create

This automatically added the Heroku remote for our app (git@heroku.com:simple-spring-9999.git) to our repository. Now we can do a simple git push to deploy our application:

::

    git push heroku master


The heroku django needs the environmental variables too (DATABASE_URL is already set on heroku) so we'll send over the values set locally:

::

    heroku config:add PRJ_ENV=production
    heroku config:add PRJ_SECRET_KEY=YOR_SECRET_KEY


Let’s ensure we have one dyno running the web process type:

::

    heroku ps:scale web=1

You can check the state of the app’s dynos. The heroku ps command lists the running dynos of your application:

::

    heroku ps

Here, one dyno is running. We can now visit the app in our browser with heroku open.

::

    heroku open

Syncing the database.
The heroku run command lets you run one-off admin dynos. You can use this to sync the Django models with the database schema:

::

    heroku run python manage.py syncdb --all
    heroku run python manage.py migrate --fake


When deploying:
---------------

TODO


================
Acknowledgements
================

    - https://github.com/twoscoops/django-twoscoops-project
    - https://github.com/torchbox/vagrant-django-template
    - https://zapier.com/engineering/profiling-python-boss/
