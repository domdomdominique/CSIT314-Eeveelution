from app.entity.favourite import Favourite
from app.entity.idp import IDP


class ViewIDPController:
    """Control: handles the Customer 'View IDP' use case (C-06)."""

    def view(self, idp_id, customer_id=None):
        idp = IDP.get(idp_id)
        if idp is None or idp.designer.is_suspended:
            raise LookupError("Project not found.")
        idp.record_view()  # feeds the designer's view statistics (ID-13)
        saved_ids = Favourite.saved_idp_ids(customer_id) if customer_id else set()
        return {
            "idp": idp,
            "designer": idp.designer,
            "project_count": IDP.count_for_designer(idp.designer_id),
            "more": IDP.more_by_designer(idp.designer_id, idp.id),
            "saved": idp.id in saved_ids,
            "saved_ids": saved_ids,
        }
