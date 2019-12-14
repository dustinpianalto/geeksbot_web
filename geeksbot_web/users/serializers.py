from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta

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
            prev_usernames = set(instance.previous_usernames or [])
            prev_usernames.add(instance.username)
            validated_data['previous_usernames'] = list(prev_usernames)
        if 'discriminator' in validated_data and instance.discriminator != validated_data['discriminator']:
            prev_discrims = set(instance.previous_discriminators or [])
            prev_discrims.add(instance.discriminator)
            validated_data['previous_discriminators'] = list(prev_discrims)
        if 'guild' in validated_data and 'guilds' not in validated_data:
            validated_data['guilds'] = [validated_data['guild']]

        # Copied with slight changes from super.update()
        raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save()

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            if isinstance(value, (list, tuple, set)):
                field.add(*value)
            else:
                field.add(value)

        return instance


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
