import re

from rest_framework import serializers


def validate_bad_value_in_username(value):
    """ "Запрет имя пользователя me"""

    if value.lower() == 'me':
        raise serializers.ValidationError(
            'Недопустимо "me" как имя пользователя'
        )
    return value


def validate_bad_signs_in_username(value):
    """Запрет на недопустимые символы"""

    if not re.match(r'^[\w.@+-]+', value):
        raise serializers.ValidationError(
            'Имя пользователя содержит недопустимые символы'
        )
    return value
