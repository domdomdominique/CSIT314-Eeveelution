from datetime import datetime

from app.entity.db import db


class Report(db.Model):
    """Entity: a customer's report that an IDP is inappropriate (reviewed by a User Admin)."""

    REASONS = (
        "Spam or advertising",
        "Wrong or misleading information",
        "Inappropriate photos or content",
        "Copied from another designer",
        "Other",
    )

    id = db.Column(db.Integer, primary_key=True)
    idp_id = db.Column(db.Integer, db.ForeignKey("idp.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("user_account.id"), nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="open", nullable=False)  # open / resolved
    created_at = db.Column(db.DateTime, default=datetime.now)

    idp = db.relationship("IDP")

    @classmethod
    def submit(cls, customer_id, idp_id, reason, details=""):
        report = cls(customer_id=customer_id, idp_id=idp_id, reason=reason, details=details)
        db.session.add(report)
        db.session.commit()
        return report

    @classmethod
    def count_open(cls):
        return cls.query.filter_by(status="open").count()
