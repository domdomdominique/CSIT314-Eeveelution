from app.entity.favourite import Favourite
from app.entity.idp import IDP
from app.entity.user_account import UserAccount


class ViewLandingPageController:
    """Control: gathers everything the public landing page shows."""

    def view(self, sort="views", customer_id=None):
        sort = "newest" if sort == "newest" else "views"
        counts = IDP.count_by_category()
        return {
            "sort": sort,
            "popular": IDP.popular(sort),
            "categories": [(name, counts.get(name, 0)) for name in IDP.CATEGORIES],
            "featured": [self._designer_card(UserAccount.get(i)) for i in IDP.top_designer_ids()],
            "customer_count": UserAccount.count_by_role("customer"),
            "designer_count": UserAccount.count_by_role("designer"),
            "saved_ids": Favourite.saved_idp_ids(customer_id) if customer_id else set(),
        }

    @staticmethod
    def _designer_card(designer):
        return {"designer": designer, "project_count": IDP.count_for_designer(designer.id)}
