import os


class Config:
    """
    Configuration class for the Flask application.
    Contains default settings and allows for environment variable overrides.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'SECRET_KEY'
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = '.flask_session'

class TestingConfig(Config):
    TESTING = True
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = '.test_flask_session'
