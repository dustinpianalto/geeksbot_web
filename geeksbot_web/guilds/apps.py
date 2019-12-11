from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GuildsConfig(AppConfig):
    name = 'geeksbot_web.guilds'
    verbose_name = _("Guilds")
