from rest_framework import serializers

from geeksbot_web.patreon.models import PatreonCreator
from geeksbot_web.patreon.models import PatreonTier


class PatreonCreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatreonCreator
        fields = "__all__"


class PatreonTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatreonTier
        fields = "__all__"
