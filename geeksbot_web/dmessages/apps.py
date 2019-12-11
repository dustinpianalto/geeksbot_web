from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MessagesConfig(AppConfig):
    name = 'geeksbot_web.dmessages'
    verbose_name = _("DMessages")
