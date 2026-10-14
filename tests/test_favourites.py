import pytest

from app.control.remove_favourite_controller import RemoveFavouriteController
from app.control.save_favourite_controller import SaveFavouriteController
from app.control.search_favourites_controller import SearchFavouritesController
from app.control.view_favourites_controller import ViewFavouritesController
from app.entity.db import db
from app.entity.idp import IDP
from app.entity.user_account import UserAccount


def setup_data():
    designer = UserAccount.create("des@test.com", "password123", "designer")
    customer = UserAccount.create("cus@test.com", "password123", "customer", name="Sarah Tan")
    loft = IDP(title="Scandinavian Loft", category="Living Room", designer_id=designer.id, view_count=10)
    kitchen = IDP(title="Modern Kitchen", category="Kitchen", designer_id=designer.id, view_count=99)
    db.session.add_all([loft, kitchen])
    db.session.commit()
    return customer, loft, kitchen


def login(client, email="cus@test.com"):
    client.post("/login", data={"email": email, "password": "password123"})


# --- C-11 Save -----------------------------------------------------------

def test_save_adds_favourite_and_counts_it_once(app):
    customer, loft, _ = setup_data()
    controller = SaveFavouriteController()
    controller.save(customer.id, loft.id)
    controller.save(customer.id, loft.id)  # saving twice is harmless
    assert ViewFavouritesController().count(customer.id) == 1
    assert loft.shortlist_count == 1


def test_save_unknown_project_raises(app):
    customer, _, _ = setup_data()
    with pytest.raises(LookupError):
        SaveFavouriteController().save(customer.id, 999)


# --- C-12 View / C-13 Search ---------------------------------------------

def test_view_sorts_favourites(app):
    customer, loft, kitchen = setup_data()
    SaveFavouriteController().save(customer.id, loft.id)
    SaveFavouriteController().save(customer.id, kitchen.id)
    view = ViewFavouritesController()
    assert [p.title for p in view.view(customer.id, "views")] == ["Modern Kitchen", "Scandinavian Loft"]
    assert [p.title for p in view.view(customer.id, "title")] == ["Modern Kitchen", "Scandinavian Loft"]


def test_search_only_looks_in_own_favourites(app):
    customer, loft, kitchen = setup_data()
    other = UserAccount.create("other@test.com", "password123", "customer")
    SaveFavouriteController().save(customer.id, loft.id)
    SaveFavouriteController().save(other.id, kitchen.id)
    search = SearchFavouritesController()
    assert [p.title for p in search.search(customer.id, "living")] == ["Scandinavian Loft"]
    assert search.search(customer.id, "kitchen") == []


# --- C-14 Remove ---------------------------------------------------------

def test_remove_deletes_favourite_and_lowers_count(app):
    customer, loft, _ = setup_data()
    SaveFavouriteController().save(customer.id, loft.id)
    RemoveFavouriteController().remove(customer.id, loft.id)
    assert ViewFavouritesController().count(customer.id) == 0
    assert loft.shortlist_count == 0


# --- Pages ---------------------------------------------------------------

def test_favourites_page_needs_login_and_returns_after(client, app):
    setup_data()
    response = client.get("/customer/favourites")
    assert response.status_code == 302
    assert "next=/customer/favourites" in response.headers["Location"]

    response = client.post("/login?next=/customer/favourites",
                           data={"email": "cus@test.com", "password": "password123"})
    assert response.headers["Location"] == "/customer/favourites"


def test_login_ignores_offsite_next(client, app):
    setup_data()
    response = client.post("/login?next=//evil.example",
                           data={"email": "cus@test.com", "password": "password123"})
    assert response.headers["Location"] == "/customer/"


def test_heart_buttons_save_remove_and_undo(client, app):
    customer, loft, _ = setup_data()
    login(client)
    client.post(f"/customer/favourites/{loft.id}", data={"next": "/"})
    page = client.get("/customer/favourites?q=loft").get_data(as_text=True)
    assert "Scandinavian Loft" in page

    response = client.post(f"/customer/favourites/{loft.id}/remove",
                           data={"next": "/customer/favourites"}, follow_redirects=True)
    page = response.get_data(as_text=True)
    assert "Removed “Scandinavian Loft” from favourites" in page
    assert "Undo" in page
    assert ViewFavouritesController().count(customer.id) == 0


def test_designer_cannot_save_favourites(client, app):
    _, loft, _ = setup_data()
    login(client, "des@test.com")
    assert client.post(f"/customer/favourites/{loft.id}").status_code == 403
