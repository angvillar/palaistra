# palaistra/palaistra/settings/prod.py
import os
from .base import *

# Production-specific settings
# Ensure DEBUG is False for security
#DEBUG = False

# In production, you must specify which hosts can serve your site. This should be
# read from an environment variable for security.
#ALLOWED_HOSTS_str = os.getenv('DJANGO_ALLOWED_HOSTS')
#ALLOWED_HOSTS = ALLOWED_HOSTS_str.split(',') if ALLOWED_HOSTS_str else []

# --- Production Database ---
# Use a separate SQLite database for production to keep data isolated.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # The BASE_DIR is inherited from base.py
        'NAME': BASE_DIR / 'prod_db.sqlite3',
    }
}

# Add any other production-only settings here. For example:
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True

"""
For Production: On your production server, you need to set the DJANGO_ENV environment variable to production. You also must set DJANGO_SECRET_KEY and DJANGO_ALLOWED_HOSTS.

Example of how you might run your server in production:

export DJANGO_ENV=production
export DJANGO_SECRET_KEY='a-very-long-and-secure-random-string'
export DJANGO_ALLOWED_HOSTS='yourdomain.com,www.yourdomain.com'

gunicorn palaistra.wsgi
"""