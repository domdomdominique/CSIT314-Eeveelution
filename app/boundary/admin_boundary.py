from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from app.boundary import role_required
from app.control.review_designer_application_controller import ReviewDesignerApplicationController

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@role_required("admin")
def home():
    pending = ReviewDesignerApplicationController().pending_count()
    return render_template("admin/home.html", pending=pending)


@admin_bp.route("/applications")
@role_required("admin")
def applications():
    """Boundary: DesignerApplicationListPage."""
    controller = ReviewDesignerApplicationController()
    status = request.args.get("status", "pending")
    return render_template(
        "admin/applications.html",
        applications=controller.list_applications(status),
        status=status,
        pending=controller.pending_count(),
    )


@admin_bp.route("/applications/<int:application_id>")
@role_required("admin")
def application_detail(application_id):
    """Boundary: DesignerApplicationPage (approve or reject)."""
    application = ReviewDesignerApplicationController().get(application_id)
    if application is None:
        abort(404)
    return render_template("admin/application_detail.html", application=application)


@admin_bp.route("/applications/<int:application_id>/approve", methods=["POST"])
@role_required("admin")
def approve_application(application_id):
    try:
        account = ReviewDesignerApplicationController().approve(application_id, session["user_id"])
    except ValueError as error:
        flash(str(error))
    else:
        flash(f"Approved. Designer account created for {account.email}.")
    return redirect(url_for("admin.applications"))


@admin_bp.route("/applications/<int:application_id>/reject", methods=["POST"])
@role_required("admin")
def reject_application(application_id):
    try:
        ReviewDesignerApplicationController().reject(
            application_id, session["user_id"], request.form.get("reason")
        )
    except ValueError as error:
        flash(str(error))
    else:
        flash("Application rejected.")
    return redirect(url_for("admin.applications"))
