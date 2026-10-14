from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from app.boundary import role_required, safe_next
from app.control.browse_designers_controller import BrowseDesignersController
from app.control.remove_favourite_controller import RemoveFavouriteController
from app.control.save_favourite_controller import SaveFavouriteController
from app.control.search_favourites_controller import SearchFavouritesController
from app.control.search_idp_controller import SearchIDPController
from app.control.view_designer_profile_controller import ViewDesignerProfileController
from app.control.view_favourites_controller import ViewFavouritesController

customer_bp = Blueprint("customer", __name__, url_prefix="/customer")


def _customer_id():
    """The logged-in customer's id, or None for visitors and other roles."""
    return session["user_id"] if session.get("role") == "customer" else None


@customer_bp.route("/")
@role_required("customer")
def home():
    """Boundary: SearchIDPPage (customer home)."""
    # The landing page search bar sends a keyword and/or a category dropdown value
    keyword = request.args.get("q") or request.args.get("category", "")
    results = SearchIDPController().search(keyword)
    return render_template("customer/search_idp.html", results=results, keyword=keyword)


# --- Favourites (C-11 to C-14) -----------------------------------------------

@customer_bp.route("/favourites")
@role_required("customer")
def favourites():
    """Boundary: MyFavouritesPage (C-12 view, C-13 search)."""
    view = ViewFavouritesController()
    keyword = request.args.get("q", "").strip()
    sort = view.clean_sort(request.args.get("sort"))
    if keyword:
        projects = SearchFavouritesController().search(session["user_id"], keyword, sort)
    else:
        projects = view.view(session["user_id"], sort)
    return render_template(
        "customer/favourites.html", projects=projects, keyword=keyword, sort=sort,
        sorts=view.sort_options(), total=view.count(session["user_id"]),
    )


@customer_bp.route("/favourites/<int:idp_id>", methods=["POST"])
@role_required("customer")
def save_favourite(idp_id):
    """Boundary: heart button on an IDP card (C-11)."""
    try:
        SaveFavouriteController().save(session["user_id"], idp_id)
    except LookupError:
        abort(404)
    return redirect(safe_next(request.form.get("next")) or url_for("customer.favourites"))


@customer_bp.route("/favourites/<int:idp_id>/remove", methods=["POST"])
@role_required("customer")
def remove_favourite(idp_id):
    """Boundary: orange heart on a saved IDP card (C-14). Offers an Undo."""
    try:
        idp = RemoveFavouriteController().remove(session["user_id"], idp_id)
    except LookupError:
        abort(404)
    flash({"text": f"Removed “{idp.title}” from favourites", "undo_idp": idp.id}, "toast")
    return redirect(safe_next(request.form.get("next")) or url_for("customer.favourites"))


# --- Designers (public) ---------------------------------------------------------

@customer_bp.route("/designers")
def designers():
    """Boundary: BrowseDesignersPage."""
    return render_template("customer/designers.html",
                           designers=BrowseDesignersController().list_designers())


@customer_bp.route("/designers/<int:designer_id>")
def designer_profile(designer_id):
    """Boundary: DesignerProfilePage (C-10)."""
    try:
        page = ViewDesignerProfileController().view(
            designer_id, request.args.get("status"), _customer_id())
    except LookupError:
        abort(404)
    return render_template("customer/designer_profile.html",
                           show_all=request.args.get("all") == "1", **page)
