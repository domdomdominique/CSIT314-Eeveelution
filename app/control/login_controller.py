from app.entity.designer_application import DesignerApplication
from app.entity.user_account import UserAccount


class LoginController:
    """Control: handles the 'Log in' use case for every actor."""

    def login(self, email, password):
        return UserAccount.login((email or "").strip().lower(), password)

    def application_status(self, email):
        """Status of a designer application for an email with no account yet, else None."""
        email = (email or "").strip().lower()
        if UserAccount.email_exists(email):
            return None
        application = DesignerApplication.latest_for(email)
        return application.status if application else None
