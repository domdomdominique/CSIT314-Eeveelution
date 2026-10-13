"""Shared input checks for the two sign-up use cases.

Each function returns the cleaned value or raises ValueError with a
message the boundary can show to the user.
"""
import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SG_PHONE_RE = re.compile(r"^[3689]\d{7}$")
UEN_RE = re.compile(r"^[0-9A-Z]{9,10}$")
MIN_PASSWORD_LENGTH = 8


def clean_name(name):
    name = (name or "").strip()
    if not name:
        raise ValueError("Please enter your name.")
    return name


def clean_email(email):
    email = (email or "").strip().lower()
    if not EMAIL_RE.match(email):
        raise ValueError("Please enter a valid email address.")
    return email


def clean_phone(phone):
    """Accept '91234567', '9123 4567' or '+65 9123 4567'; store as '+65 91234567'."""
    digits = re.sub(r"[\s-]", "", phone or "")
    if digits.startswith("+65"):
        digits = digits[3:]
    if not SG_PHONE_RE.match(digits):
        raise ValueError("Please enter an 8-digit Singapore phone number.")
    return f"+65 {digits}"


def check_password(password, confirm_password):
    if len(password or "") < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
    if password != confirm_password:
        raise ValueError("Passwords do not match.")


def clean_uen(uen):
    uen = (uen or "").strip().upper()
    if not UEN_RE.match(uen):
        raise ValueError("Please enter a valid UEN (9 or 10 letters/digits).")
    return uen
