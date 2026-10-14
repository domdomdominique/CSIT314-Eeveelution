from app.entity.favourite import Favourite
from app.entity.idp import IDP


class SaveFavouriteController:
    """Control: handles the Customer 'Favourite IDPs' use case (C-07)."""

    def save(self, customer_id, idp_id):
        idp = IDP.get(idp_id)
        if idp is None:
            raise LookupError("Project not found.")
        Favourite.add(customer_id, idp)
        return idp
