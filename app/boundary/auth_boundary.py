from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.control.apply_designer_controller import ApplyDesignerController
from app.control.login_controller import LoginController
from app.control.register_controller import RegisterController

auth_bp = Blueprint("auth", __name__)

HOME_BY_ROLE = {
    "admin": "admin.home",
    "designer": "designer.home",
    "customer": "customer.home",
    "platform": "platform.home",
}

APPLICATION_MESSAGES = {
    "pending": "Your designer application is still being reviewed. "
               "You can log in once an admin approves it.",
    "rejected": "Your designer application was not approved. "
                "Please contact us or apply again.",
}


@auth_bp.route("/")
def index():
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Boundary: LoginPage."""
    if request.method == "POST":
        controller = LoginController()
        account = controller.login(request.form["email"], request.form["password"])
        if account:
            session["user_id"] = account.id
            session["role"] = account.role
            return redirect(url_for(HOME_BY_ROLE[account.role]))
        status = controller.application_status(request.form["email"])
        flash(APPLICATION_MESSAGES.get(status, "Invalid email or password."))
    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Boundary: RegisterPage (customer sign-up, account is active immediately)."""
    if request.method == "POST":
        f = request.form
        try:
            RegisterController().register(
                f.get("name"), f.get("email"), f.get("phone"),
                f.get("password"), f.get("confirm_password"),
            )
        except ValueError as error:
            flash(str(error))
        else:
            flash("Account created! Please log in.")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html", account_type="customer", form=request.form)


@auth_bp.route("/register/designer", methods=["GET", "POST"])
def apply_designer():
    """Boundary: ApplyDesignerPage (application goes to the User Admin for approval)."""
    if request.method == "POST":
        f = request.form
        try:
            ApplyDesignerController().apply(
                f.get("name"), f.get("email"), f.get("phone"),
                f.get("password"), f.get("confirm_password"),
                f.get("company_name"), f.get("uen"), f.get("portfolio_url"),
                f.get("experience_years"), f.get("description"),
            )
        except ValueError as error:
            flash(str(error))
        else:
            flash("Application submitted! An admin will review it, "
                  "and you can log in once it is approved.")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html", account_type="designer", form=request.form)


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
