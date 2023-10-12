import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'SECRET_KEY'
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = '.flask_session'
