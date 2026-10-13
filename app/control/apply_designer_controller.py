from app.control.signup_validation import (
    check_password, clean_email, clean_name, clean_phone, clean_uen,
)
from app.entity.designer_application import DesignerApplication
from app.entity.user_account import UserAccount


class ApplyDesignerController:
    """Control: handles the Interior Designer 'Apply for account' use case."""

    def apply(self, name, email, phone, password, confirm_password,
              company_name, uen, portfolio_url="", experience_years="0", description=""):
        name = clean_name(name)
        email = clean_email(email)
        phone = clean_phone(phone)
        check_password(password, confirm_password)
        company_name = (company_name or "").strip()
        if not company_name:
            raise ValueError("Please enter your company name.")
        uen = clean_uen(uen)
        try:
            experience_years = int(experience_years or 0)
        except ValueError:
            raise ValueError("Years of experience must be a number.")
        if experience_years < 0:
            raise ValueError("Years of experience cannot be negative.")

        portfolio_url = (portfolio_url or "").strip()
        if portfolio_url and not portfolio_url.startswith(("http://", "https://")):
            raise ValueError("Portfolio link must start with http:// or https://")

        if UserAccount.email_exists(email):
            raise ValueError("Email already registered.")
        if DesignerApplication.has_pending(email):
            raise ValueError("You already have an application waiting for review.")

        return DesignerApplication.submit(
            name, email, phone, password, company_name, uen,
            portfolio_url=portfolio_url,
            experience_years=experience_years,
            description=(description or "").strip(),
        )
