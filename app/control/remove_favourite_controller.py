from app.entity.favourite import Favourite
from app.entity.idp import IDP


class RemoveFavouriteController:
    """Control: handles the Customer 'Remove IDP from favourites' use case (C-10)."""

    def remove(self, customer_id, idp_id):
        idp = IDP.get(idp_id)
        if idp is None:
            raise LookupError("Project not found.")
        Favourite.remove(customer_id, idp)
        return idp
