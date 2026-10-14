from app.entity.designer_application import DesignerApplication
from app.entity.user_account import UserAccount


class LoginController:
    """Control: handles the 'Log in' use case for every actor."""

    def login(self, email, password, role=None):
        """The account if the details are valid (and match the chosen role, if any), else None."""
        account = UserAccount.login((email or "").strip().lower(), password)
        if account and role and account.role != role:
            return None
        return account

    def application_status(self, email):
        """Status of a designer application for an email with no account yet, else None."""
        email = (email or "").strip().lower()
        if UserAccount.email_exists(email):
            return None
        application = DesignerApplication.latest_for(email)
        return application.status if application else None
