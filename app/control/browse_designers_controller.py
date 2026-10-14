from app.entity.idp import IDP
from app.entity.user_account import UserAccount


class BrowseDesignersController:
    """Control: lists designers who have projects, busiest first."""

    def list_designers(self, limit=60):
        designers = [UserAccount.get(i) for i in IDP.top_designer_ids(limit)]
        return [{"designer": d, "project_count": IDP.count_for_designer(d.id)} for d in designers]
