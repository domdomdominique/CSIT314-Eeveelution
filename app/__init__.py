import os

from flask import Flask

from app.entity.db import db

# Development-only key so the app works out of the box for the whole group.
# For a real deployment, set the ENCRYPTION_KEY environment variable to a key
# made with:  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
DEV_ENCRYPTION_KEY = "1dCtVD-SSy_dupVpi3OPSN3pxR6kAqcWwtK4vMg-NPA="


def create_app(test_config=None):
    """Application factory: builds and configures the Flask app."""
    app = Flask(__name__, template_folder="boundary/templates")
    app.config.update(
        SECRET_KEY="dev-change-me",
        SQLALCHEMY_DATABASE_URI="sqlite:///eeveelution.db",
        ENCRYPTION_KEY=os.environ.get("ENCRYPTION_KEY", DEV_ENCRYPTION_KEY),
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    # Boundary layer: one blueprint per actor
    from app.boundary.auth_boundary import auth_bp
    from app.boundary.customer_boundary import customer_bp
    from app.boundary.admin_boundary import admin_bp
    from app.boundary.designer_boundary import designer_bp
    from app.boundary.platform_boundary import platform_bp

    for bp in (auth_bp, customer_bp, admin_bp, designer_bp, platform_bp):
        app.register_blueprint(bp)

    with app.app_context():
        db.create_all()

    return app
