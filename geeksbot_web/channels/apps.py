from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ChannelsConfig(AppConfig):
    name = 'geeksbot_web.channels'
    verbose_name = _("Channels")
