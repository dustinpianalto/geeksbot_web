from django.contrib.auth.validators import UnicodeUsernameValidator


class CustomUsernameValidator(UnicodeUsernameValidator):
    regex = r'^[\X]+$'
