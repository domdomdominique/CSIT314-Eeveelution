import pytest
from cryptography.fernet import Fernet

from app.control.apply_designer_controller import ApplyDesignerController
from app.control.register_controller import RegisterController
from app.entity.db import db
from app.entity.user_account import UserAccount


def raw_phone(table):
    """Read the phone column straight from SQLite, skipping decryption."""
    return db.session.execute(db.text(f"SELECT phone FROM {table}")).scalar()


def register_amy():
    return RegisterController().register("Amy Tan", "amy@test.com", "9123 4567",
                                         "password123", "password123")


def test_customer_phone_is_encrypted_in_database(app):
    register_amy()
    stored = raw_phone("user_account")
    assert "91234567" not in stored
    assert stored.startswith("gAAAAA")  # Fernet token


def test_app_reads_phone_back_as_plain_text(app):
    register_amy()
    db.session.expire_all()  # force a fresh read from the database
    assert UserAccount.query.first().phone == "+65 91234567"


def test_designer_application_phone_is_encrypted(app):
    ApplyDesignerController().apply(
        "Ben Lim", "ben@studio.com", "8765 4321", "designer123", "designer123",
        "Oak Studio", "201912345K",
    )
    assert "87654321" not in raw_phone("designer_application")


def test_same_phone_encrypts_differently_each_time(app):
    register_amy()
    RegisterController().register("Bob Ng", "bob@test.com", "9123 4567",
                                  "password123", "password123")
    first, second = db.session.execute(db.text("SELECT phone FROM user_account")).scalars()
    assert first != second


def test_wrong_key_cannot_read_phone(app):
    register_amy()
    db.session.expire_all()
    app.config["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
    with pytest.raises(ValueError, match="Could not decrypt"):
        UserAccount.query.first().phone
