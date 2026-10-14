from app.entity.favourite import Favourite
from app.entity.idp import IDP


class SaveFavouriteController:
    """Control: handles the Customer 'Save IDP to favourites' use case (C-11)."""

    def save(self, customer_id, idp_id):
        idp = IDP.get(idp_id)
        if idp is None:
            raise LookupError("Project not found.")
        Favourite.add(customer_id, idp)
        return idp
