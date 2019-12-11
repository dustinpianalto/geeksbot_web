from django.contrib import admin

from geeksbot_web.guilds.models import Guild
from geeksbot_web.guilds.models import Role

# Register your models here.
admin.site.register(Guild)
admin.site.register(Role)