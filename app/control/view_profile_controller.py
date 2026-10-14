from app.entity.user_account import UserAccount


class ViewProfileController:
    """Control: handles the Customer 'View Customer Profile' use case (C-11)."""

    def view(self, account_id):
        account = UserAccount.get(account_id)
        if account is None:
            raise LookupError("Account not found.")
        return account
