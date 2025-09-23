# palaistra/palaistra/settings/local_prod.py
from .dev import *

# Override the database setting to use the production database
# This is useful for debugging production data locally.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # The BASE_DIR is inherited from base.py
        'NAME': BASE_DIR / 'prod_db.sqlite3',
    }
}