import os

# Get the environment from the DJANGO_ENV environment variable.
# Default to 'development' for local work, 'production' is safer for servers.
ENVIRONMENT = os.getenv('DJANGO_ENV', 'dev')

# Dynamically import the correct settings file
if ENVIRONMENT == 'dev':
    from .dev import *
elif ENVIRONMENT == 'local_prod': # Same as dev but used the prod db
    from .local_prod import *
else: # Default to production settings for safety
    from .prod import *