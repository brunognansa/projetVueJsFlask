from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()
mail = Mail()
cors = CORS()

def create_app(config=None):
    app = Flask(__name__)

    # Load configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL' ,'postgresql://username:password@host:port/database_name'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'jwt_dev_key'),
        JWT_ACCESS_TOKEN_EXPIRES=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 900)),  # 15 minutes
        JWT_REFRESH_TOKEN_EXPIRES=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000)),  # 30 days
        MAIL_SERVER=os.environ.get('MAIL_SERVER', 'smtp.example.com'),
        MAIL_PORT=int(os.environ.get('MAIL_PORT', 587)),
        MAIL_USE_TLS=os.environ.get('MAIL_USE_TLS', 'True').lower() in ('true', '1', 't'),
        MAIL_USERNAME=os.environ.get('MAIL_USERNAME', 'user@example.com'),
        MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD', 'password'),
        MAIL_DEFAULT_SENDER=os.environ.get('MAIL_DEFAULT_SENDER', 'library@example.com')
    )

    # Override config if provided
    if config:
        app.config.update(config)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    cors.init_app(app)

    # Register blueprints
    from app.controllers.auth_controller import auth_bp
    from app.controllers.book_controller import book_bp
    from app.controllers.loan_controller import loan_bp
    from app.controllers.user_controller import user_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(book_bp, url_prefix='/books')
    app.register_blueprint(loan_bp, url_prefix='/loans')
    app.register_blueprint(user_bp, url_prefix='/users')

    # Register error handlers
    from app.utils.error_handler import enregistrer_gestionnaires_erreurs
    enregistrer_gestionnaires_erreurs(app)

    return app
