from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RconConfig(AppConfig):
    name = 'geeksbot_web.rcon'
    verbose_name = _("Rcon")
