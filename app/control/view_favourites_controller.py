from app.entity.favourite import Favourite


class ViewFavouritesController:
    """Control: handles the Customer 'View favourites' use case (C-12)."""

    def view(self, customer_id, sort="recent"):
        return Favourite.list_for(customer_id, sort=self.clean_sort(sort))

    def count(self, customer_id):
        return Favourite.count_for(customer_id)

    @staticmethod
    def clean_sort(sort):
        return sort if sort in Favourite.SORTS else "recent"

    @staticmethod
    def sort_options():
        return Favourite.SORTS
