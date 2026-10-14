from app.control.signup_validation import clean_email, clean_phone
from app.entity.designer_application import DesignerApplication
from app.entity.user_account import UserAccount


class UpdateProfileController:
    """Control: handles the Customer 'Update Customer Profile' use case (C-12)."""

    def update(self, account_id, first_name, last_name, email, phone):
        account = UserAccount.get(account_id)
        if account is None:
            raise LookupError("Account not found.")
        first_name, last_name = (first_name or "").strip(), (last_name or "").strip()
        if not first_name:
            raise ValueError("Please enter your first name.")
        email = clean_email(email)
        phone = clean_phone(phone)
        if email != account.email and (UserAccount.email_exists(email)
                                       or DesignerApplication.has_pending(email)):
            raise ValueError("That email is already used by another account.")
        account.update_details(f"{first_name} {last_name}".strip(), email, phone)
        return account
