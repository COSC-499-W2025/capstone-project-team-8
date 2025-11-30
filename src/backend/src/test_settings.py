from .settings import *
import gc

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

# Force garbage collection after each test
class TestRunnerWithGC:
    def __init__(self, *args, **kwargs):
        from django.test.runner import DiscoverRunner
        self.runner = DiscoverRunner(*args, **kwargs)
    
    def run_tests(self, *args, **kwargs):
        result = self.runner.run_tests(*args, **kwargs)
        gc.collect()
        return result

TEST_RUNNER = 'src.test_settings.TestRunnerWithGC'