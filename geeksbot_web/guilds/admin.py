from django.contrib import admin

from guilds.models import Guild
from guilds.models import Role

# Register your models here.
admin.site.register(Guild)
admin.site.register(Role)