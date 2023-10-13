import shutil

from flask_testing import TestCase

from app import create_app
from app.config import TestingConfig


class BaseTestCase(TestCase):
    def create_app(self):
        app = create_app(TestingConfig)
        return app

    def setUp(self):
        # Called before every test. You can set up test data here.
        pass

    def tearDown(self):
        # Remove the session files directory after all tests have run
        shutil.rmtree('.test_flask_session', ignore_errors=True)
