from flask import Flask

from config import Config
from app.extensions import db, bcrypt, migrate, cors, jwt

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    cors.init_app(app)
    jwt.init_app(app)

    # Register blueprints here
    from app.files import bp as files_bp
    app.register_blueprint(files_bp)

    from app.users import bp as users_bp
    app.register_blueprint(users_bp)

    from app.chats import bp as chats_bp
    app.register_blueprint(chats_bp)

    return app