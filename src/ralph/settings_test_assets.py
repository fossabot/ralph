#
# A testing profile.
#

from ralph.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'OPTIONS': {},
    }
}
print INSTALLED_APPS

PLUGGABLE_APPS = ['cmdb', 'assets']

SOUTH_TESTS_MIGRATE = False

ASSETS_AUTO_ASSIGN_HOSTNAME = True
