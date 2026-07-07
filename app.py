import os
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager

load_dotenv()

from config import Config
from models import db
from models.user import User
from models.recruiter import Recruiter


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(composite_id):
        try:
            kind, raw_id = composite_id.split("-", 1)
        except ValueError:
            return None

        if kind == "user":
            return User.query.get(int(raw_id))
        elif kind == "recruiter":
            return Recruiter.query.get(int(raw_id))
        return None

    from routes.main_routes import main_bp
    from routes.auth_routes import auth_bp
    from routes.candidate_routes import candidate_bp
    from routes.recruiter_routes import recruiter_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(recruiter_bp)
    app.register_blueprint(admin_bp)

    @app.errorhandler(403)
    def forbidden(e):
        return "Access denied: you don't have permission to view this page.", 403

    @app.errorhandler(404)
    def not_found(e):
        return "Page not found.", 404

    with app.app_context():
        db.create_all()
        _ensure_default_admin()

    return app


def _ensure_default_admin():
    """Creates a default admin account on first run if none exists."""
    admin = User.query.filter_by(role="admin").first()
    if not admin:
        admin = User(fullname="System Admin", email="admin@smarthire.ai", role="admin")
        admin.set_password("Admin@123")
        db.session.add(admin)
        db.session.commit()
        print("Default admin created -> email: admin@smarthire.ai | password: Admin@123")


app = create_app()

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
