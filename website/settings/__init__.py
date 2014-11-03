import os, sys

########################################################################
# Importing the appropriate settings file for this environment
########################################################################
ENVIRONMENT = os.getenv("DJANGO_ENVIRONMENT")
if not ENVIRONMENT:
    ENVIRONMENT = 'dev'

if ENVIRONMENT == 'production':
    from production import *
elif ENVIRONMENT == 'dev':
    from dev import *
elif ENVIRONMENT == 'staging':
    from staging import *

# Try importing the local setting file (this shouldn't be kept in version
# control). It can have settings that are specific to this machine, or if you
# don't want passwords/etc kept in the version control can set them in the
# local
try:
    from local import *
except ImportError:
    # No local settings which is fine
    pass
