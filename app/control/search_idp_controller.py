from app.entity.idp import IDP


class SearchIDPController:
    """Control: handles the Customer 'Search IDPs' (C-04), 'Filter IDPs by
    category' (C-05) and 'Sort IDP' (C-17) use cases."""

    SORTS = {"views": "Most viewed", "newest": "Newest"}
    STATUSES = {"current": "Current projects", "past": "Past projects"}

    def search(self, keyword):
        return IDP.search(keyword)

    def browse(self, keyword="", categories=(), status=None, sort="views"):
        return IDP.browse(
            keyword=(keyword or "").strip(),
            categories=[c for c in categories if c in IDP.CATEGORIES],
            status=status if status in self.STATUSES else None,
            sort=self.clean_sort(sort),
        )

    def clean_sort(self, sort):
        return sort if sort in self.SORTS else "views"

    def category_counts(self):
        counts = IDP.count_by_category()
        return [(name, counts.get(name, 0)) for name in IDP.CATEGORIES]

    def status_counts(self):
        counts = IDP.count_by_status()
        return [(key, label, counts[key]) for key, label in self.STATUSES.items()]
