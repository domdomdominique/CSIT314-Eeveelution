from app.control.signup_validation import check_password, clean_email, clean_name, clean_phone
from app.entity.designer_application import DesignerApplication
from app.entity.user_account import UserAccount


class RegisterController:
    """Control: handles the Customer 'Register account' use case."""

    def register(self, name, email, phone, password, confirm_password):
        name = clean_name(name)
        email = clean_email(email)
        phone = clean_phone(phone)
        check_password(password, confirm_password)
        if UserAccount.email_exists(email) or DesignerApplication.has_pending(email):
            raise ValueError("Email already registered.")
        return UserAccount.create(email, password, "customer", name=name, phone=phone)
