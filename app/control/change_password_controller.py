from app.control.signup_validation import check_password
from app.entity.user_account import UserAccount


class ChangePasswordController:
    """Control: handles the Customer 'Change Customer Account Password' use case (C-14)."""

    def change(self, account_id, current_password, new_password, confirm_password):
        account = UserAccount.get(account_id)
        if account is None:
            raise LookupError("Account not found.")
        if not account.check_password(current_password):
            raise ValueError("Your current password is incorrect.")
        check_password(new_password, confirm_password)
        if account.check_password(new_password):
            raise ValueError("Your new password must be different from your current one.")
        account.change_password(new_password)
