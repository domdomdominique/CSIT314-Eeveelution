from datetime import datetime

from app.entity.db import db
from app.entity.idp import IDP


class Favourite(db.Model):
    """Entity: an IDP a customer has saved to their favourites (shortlist)."""

    SORTS = {
        "recent": "Recently saved",
        "views": "Most viewed",
        "title": "Title (A–Z)",
    }

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("user_account.id"), nullable=False)
    idp_id = db.Column(db.Integer, db.ForeignKey("idp.id"), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.now)

    idp = db.relationship("IDP")

    __table_args__ = (db.UniqueConstraint("customer_id", "idp_id"),)

    @classmethod
    def find(cls, customer_id, idp_id):
        return cls.query.filter_by(customer_id=customer_id, idp_id=idp_id).first()

    @classmethod
    def add(cls, customer_id, idp):
        """Save the IDP and bump its shortlist count. Returns False if already saved."""
        if cls.find(customer_id, idp.id):
            return False
        db.session.add(cls(customer_id=customer_id, idp_id=idp.id))
        idp.shortlist_count = (idp.shortlist_count or 0) + 1
        db.session.commit()
        return True

    @classmethod
    def remove(cls, customer_id, idp):
        """Unsave the IDP and lower its shortlist count. Returns False if it wasn't saved."""
        favourite = cls.find(customer_id, idp.id)
        if favourite is None:
            return False
        db.session.delete(favourite)
        idp.shortlist_count = max((idp.shortlist_count or 0) - 1, 0)
        db.session.commit()
        return True

    @classmethod
    def saved_idp_ids(cls, customer_id):
        rows = db.session.query(cls.idp_id).filter_by(customer_id=customer_id)
        return {idp_id for (idp_id,) in rows}

    @classmethod
    def count_for(cls, customer_id):
        return cls.query.filter_by(customer_id=customer_id).count()

    @classmethod
    def list_for(cls, customer_id, keyword="", sort="recent"):
        """The customer's saved IDPs, optionally filtered by title or category."""
        query = IDP.query.join(cls, cls.idp_id == IDP.id).filter(cls.customer_id == customer_id)
        if keyword:
            pattern = f"%{keyword}%"
            query = query.filter(db.or_(IDP.title.ilike(pattern), IDP.category.ilike(pattern)))
        order = {
            "views": IDP.view_count.desc(),
            "title": IDP.title.asc(),
        }.get(sort, cls.saved_at.desc())
        return query.order_by(order, cls.id.desc()).all()
