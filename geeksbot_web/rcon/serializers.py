from rest_framework import serializers

from rcon.models import RconServer


class RconServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = RconServer
        fields = "__all__"
