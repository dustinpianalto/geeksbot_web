from rest_framework import serializers

from users.models import User
from users.models import UserLog


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'name',
            'previous_usernames',
            'discriminator',
            'previous_discriminators',
            'guilds',
            'steam_id',
            'animated',
            'avatar',
            'bot',
            'banned',
            'logging_enabled',
            'is_staff',
            'is_superuser',
            'url'
        ]
        extra_kwargs = {
            'url': {
                'view_name': 'users_api:detail',
                'lookup_field': 'id'
            },
            'guilds': {
                'view_name': 'guilds_api:detail',
                'lookup_field': 'id'
            }
        }

    def update(self, instance, validated_data):
        if 'username' in validated_data and instance.username != validated_data['username']:
            prev_usernames = set(instance.previous_usernames)
            prev_usernames.add(instance.username)
            validated_data['previous_usernames'] = list(prev_usernames)
        if 'discriminator' in validated_data and instance.discriminator != validated_data['discriminator']:
            prev_discrims = set(instance.previous_discriminators)
            prev_discrims.add(instance.discriminator)
            validated_data['previous_discriminators'] = list(prev_discrims)
        super(UserSerializer, self).update(instance, validated_data)


class UserLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLog
        fields = [
            'user',
            'time',
            'action',
            'description',
            'url'
        ]
        extra_fields = {
            'url': {
                'view_name': 'users_api:log_detail',
                'lookup_field': 'id',
                'lookup_url_kwarg': 'log'
            }
        }
