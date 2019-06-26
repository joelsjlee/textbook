from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "static_page_proxy.users"
    verbose_name = _("Users")

    def ready(self):
        try:
            import static_page_proxy.users.signals  # noqa F401
        except ImportError:
            pass
