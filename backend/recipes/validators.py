import re

from django.core.exceptions import ValidationError


def validate_is_hex(string: str) -> ValidationError:
    pattern = r'^#[0-9a-fA-F]{6}$'
    if not bool(re.match(pattern, string)):
        return ValidationError('Строка не соответсвует формату hex')
