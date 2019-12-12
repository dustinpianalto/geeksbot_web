from rest_framework import serializers

from guilds.models import Guild
from guilds.models import Role


class GuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guild
        fields = "__all__"


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "guild", "role_type"]
