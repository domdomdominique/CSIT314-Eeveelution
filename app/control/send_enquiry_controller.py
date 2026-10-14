from app.entity.enquiry import Enquiry
from app.entity.idp import IDP
from app.entity.user_account import UserAccount


class SendEnquiryController:
    """Control: handles the Customer 'Contact ID' use case (C-16)."""

    MAX_MESSAGE = 2000

    def send(self, customer_id, designer_id, name, contact, message, idp_id=None):
        designer = UserAccount.get(designer_id)
        if designer is None or designer.role != "designer" or designer.is_suspended:
            raise LookupError("Designer not found.")
        name, contact, message = ((v or "").strip() for v in (name, contact, message))
        if not name:
            raise ValueError("Please enter your name.")
        if not contact:
            raise ValueError("Please enter an email or phone number the designer can reply to.")
        if not message:
            raise ValueError("Please write a message for the designer.")
        if len(message) > self.MAX_MESSAGE:
            raise ValueError(f"Please keep your message under {self.MAX_MESSAGE} characters.")
        # Only link the project if it really belongs to this designer
        idp = IDP.get(idp_id) if idp_id else None
        idp_id = idp.id if idp and idp.designer_id == designer.id else None
        Enquiry.send(designer.id, customer_id, name, contact, message, idp_id)
        return designer
