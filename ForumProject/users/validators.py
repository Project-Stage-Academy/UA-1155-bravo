import re
from string import punctuation

from rest_framework.exceptions import ValidationError


class CustomUserValidator:
    @staticmethod
    def validate_password(password):
        if len(password) < 8:
            raise ValidationError('Password length should be longer or equal than 8')
        if not any(symbol.isdigit() for symbol in password):
            raise ValidationError('Password should have at least one digit')
        if not any(symbol.isupper() for symbol in password):
            raise ValidationError('Password should have at least one uppercase letter')
        if not any(symbol.islower() for symbol in password):
            raise ValidationError('Password should have at least one lowercase letter')
        if not any(symbol in punctuation for symbol in password):
            raise ValidationError('Password should have at least one symbol')
        return password

    @staticmethod
    def validate_phone_number(phone_number):
        pattern = re.compile(r'^(\+\d{1,3})?(\d{10,12})$')
        if not pattern.match(phone_number):
            raise ValidationError('Invalid phone number')
        return phone_number
