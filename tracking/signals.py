from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from .services import log_admin_action


def client_ip(request):
    if not request:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    if user.is_staff:
        log_admin_action(user, "login", message="Admin login", ip_address=client_ip(request))


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    if user and user.is_staff:
        log_admin_action(user, "logout", message="Admin logout", ip_address=client_ip(request))
