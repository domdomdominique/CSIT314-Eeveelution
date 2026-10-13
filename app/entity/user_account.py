from werkzeug.security import check_password_hash, generate_password_hash

from app.entity.db import db
from app.entity.encryption import EncryptedString


class UserAccount(db.Model):
    """Entity: a login account for any of the four actors."""

    ROLES = ("admin", "designer", "customer", "platform")

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default="")
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(EncryptedString, default="")  # encrypted in the database
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_suspended = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    @classmethod
    def create(cls, email, password, role, name="", phone=""):
        if role not in cls.ROLES:
            raise ValueError(f"Unknown role: {role}")
        account = cls(email=email, role=role, name=name, phone=phone)
        account.set_password(password)
        db.session.add(account)
        db.session.commit()
        return account

    @classmethod
    def email_exists(cls, email):
        return cls.query.filter_by(email=email).first() is not None

    @classmethod
    def login(cls, email, password):
        """Return the account if the credentials are valid and active, else None."""
        account = cls.query.filter_by(email=email).first()
        if account is None or account.is_suspended:
            return None
        if not check_password_hash(account.password_hash, password):
            return None
        return account
