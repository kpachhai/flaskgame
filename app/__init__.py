from flask import Flask
from flask_session import Session

from .routes import game_routes


def create_app():
    app = Flask(__name__)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = '.flask_session'
    app.secret_key = 'SECRET_KEY'
    Session(app)
    
    app.register_blueprint(game_routes.game_blueprint)

    return app
