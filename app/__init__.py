from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, mail, celery
from app.routes import main_bp, auth_bp, aid_bp

def create_app():
    app = Flask(__name__, template_folder='../templates')
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    celery.conf.update(app.config)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(aid_bp)

    with app.app_context():
        db.create_all()

    return app
