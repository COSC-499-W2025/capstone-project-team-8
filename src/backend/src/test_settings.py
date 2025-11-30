from .settings import *

# Use in-memory SQLite for tests (faster and less memory)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Reduce logging during tests
LOGGING_CONFIG = None
import logging
logging.disable(logging.CRITICAL)

# Disable debug mode in tests
DEBUG = False
TEMPLATE_DEBUG = False