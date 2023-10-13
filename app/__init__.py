from flask import Flask
from flask_session import Session

from app.config import Config
from app.routes import game_routes


def create_app(config_class=Config):
    """
    Factory function to create and configure the Flask application instance.

    Args:
        config_class (Config, optional): The configuration class to use. Defaults to Config.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)
    if config_class:
        app.config.from_object(config_class)
    else:
        app.config['SESSION_TYPE'] = 'filesystem'
        app.config['SESSION_FILE_DIR'] = '.flask_session'
        app.secret_key = 'SECRET_KEY'
    Session(app)  # Initialize Flask-Session for this app

    # Register blueprints
    app.register_blueprint(game_routes.game_blueprint)

    return app
