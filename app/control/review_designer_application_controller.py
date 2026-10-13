from app.entity.designer_application import DesignerApplication


class ReviewDesignerApplicationController:
    """Control: handles the User Admin 'Review designer application' use case."""

    def list_applications(self, status="pending"):
        if status not in DesignerApplication.STATUSES:
            status = "pending"
        return DesignerApplication.list_by_status(status)

    def pending_count(self):
        return DesignerApplication.count_pending()

    def get(self, application_id):
        return DesignerApplication.get(application_id)

    def approve(self, application_id, admin_id):
        return self._find(application_id).approve(admin_id)

    def reject(self, application_id, admin_id, reason=""):
        self._find(application_id).reject(admin_id, (reason or "").strip())

    def _find(self, application_id):
        application = DesignerApplication.get(application_id)
        if application is None:
            raise ValueError("Application not found.")
        return application
