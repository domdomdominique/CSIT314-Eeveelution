from collections import Counter

from app.entity.favourite import Favourite
from app.entity.idp import IDP
from app.entity.user_account import UserAccount


class ViewDesignerProfileController:
    """Control: handles the Customer 'View designer profile' use case (C-10)."""

    def view(self, designer_id, status=None, customer_id=None):
        designer = UserAccount.get(designer_id)
        if designer is None or designer.role != "designer" or designer.is_suspended:
            raise LookupError("Designer not found.")

        all_projects = IDP.by_designer(designer.id)
        current = sum(1 for p in all_projects if p.is_current)
        categories = Counter(p.category for p in all_projects)
        total = len(all_projects)
        return {
            "designer": designer,
            "status": status if status in ("current", "past") else None,
            "projects": IDP.by_designer(designer.id, status),
            "total": total,
            "current": current,
            "past": total - current,
            "views": sum(p.view_count or 0 for p in all_projects),
            # Share of projects per category, biggest first: [(name, percent), ...]
            "category_share": [(name, round(n * 100 / total)) for name, n in categories.most_common()],
            "saved_ids": Favourite.saved_idp_ids(customer_id) if customer_id else set(),
        }
