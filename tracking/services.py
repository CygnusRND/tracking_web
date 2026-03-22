from .models import AdminAuditLog


def log_admin_action(user, action, tracking=None, event=None, message="", ip_address=None):
    AdminAuditLog.objects.create(
        admin_user=user,
        action=action,
        tracking=tracking,
        event=event,
        message=message,
        ip_address=ip_address,
    )
