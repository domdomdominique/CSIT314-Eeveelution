from datetime import datetime

from werkzeug.security import generate_password_hash

from app.entity.db import db
from app.entity.encryption import EncryptedString
from app.entity.user_account import UserAccount


class DesignerApplication(db.Model):
    """Entity: a request to open an Interior Designer account.

    A User Admin reviews it. Approving creates the designer's UserAccount
    (with the password they chose when applying); rejecting does not.
    """

    STATUSES = ("pending", "approved", "rejected")

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(EncryptedString, nullable=False)  # encrypted in the database
    password_hash = db.Column(db.String(256), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    uen = db.Column(db.String(20), nullable=False)
    portfolio_url = db.Column(db.String(255), default="")
    experience_years = db.Column(db.Integer, default=0)
    description = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="pending", nullable=False)
    rejection_reason = db.Column(db.Text, default="")
    submitted_at = db.Column(db.DateTime, default=datetime.now)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey("user_account.id"))
    account_id = db.Column(db.Integer, db.ForeignKey("user_account.id"))

    @classmethod
    def submit(cls, name, email, phone, password, company_name, uen,
               portfolio_url="", experience_years=0, description=""):
        application = cls(
            name=name, email=email, phone=phone,
            password_hash=generate_password_hash(password),
            company_name=company_name, uen=uen, portfolio_url=portfolio_url,
            experience_years=experience_years, description=description,
        )
        db.session.add(application)
        db.session.commit()
        return application

    @classmethod
    def get(cls, application_id):
        return db.session.get(cls, application_id)

    @classmethod
    def has_pending(cls, email):
        return cls.query.filter_by(email=email, status="pending").first() is not None

    @classmethod
    def latest_for(cls, email):
        return cls.query.filter_by(email=email).order_by(cls.id.desc()).first()

    @classmethod
    def list_by_status(cls, status):
        return cls.query.filter_by(status=status).order_by(cls.submitted_at).all()

    @classmethod
    def count_pending(cls):
        return cls.query.filter_by(status="pending").count()

    def approve(self, admin_id):
        """Create the designer account and mark this application approved."""
        if self.status != "pending":
            raise ValueError("This application has already been reviewed.")
        if UserAccount.email_exists(self.email):
            raise ValueError("An account with this email already exists.")
        account = UserAccount(
            name=self.name, email=self.email, phone=self.phone,
            password_hash=self.password_hash, role="designer",
        )
        db.session.add(account)
        db.session.flush()  # gives account an id before we commit
        self.account_id = account.id
        self._mark_reviewed("approved", admin_id)
        db.session.commit()  # account + application saved together
        return account

    def reject(self, admin_id, reason=""):
        if self.status != "pending":
            raise ValueError("This application has already been reviewed.")
        self.rejection_reason = reason
        self._mark_reviewed("rejected", admin_id)
        db.session.commit()

    def _mark_reviewed(self, status, admin_id):
        self.status = status
        self.reviewed_by = admin_id
        self.reviewed_at = datetime.now()
