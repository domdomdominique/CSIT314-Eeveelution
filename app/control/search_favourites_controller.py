from app.entity.favourite import Favourite


class SearchFavouritesController:
    """Control: handles the Customer 'Search Favourite List' use case (C-09)."""

    def search(self, customer_id, keyword, sort="recent"):
        sort = sort if sort in Favourite.SORTS else "recent"
        return Favourite.list_for(customer_id, keyword=(keyword or "").strip(), sort=sort)
