import re
from string import punctuation

from rest_framework.exceptions import ValidationError


class CustomUserValidator:
    """
    A utility class for validating user inputs.

    This class provides static methods to validate user passwords and phone numbers.

    Methods:
    - validate_password: Validates the format of a password string.
    - validate_phone_number: Validates the format of a phone number string.
    """
    @staticmethod
    def validate_password(password):
        """
        Validate the format of a password string.

        Parameters:
        - password (str): The password string to validate.

        Returns:
        - str: The validated password string.

        Raises:
        - ValidationError: If the password format does not meet the requirements.
        """
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
        """
        Validate the format of a phone number string.

        Parameters:
        - phone_number (str): The phone number string to validate.

        Returns:
        - str: The validated phone number string.

        Raises:
        - ValidationError: If the phone number format is invalid.
        """
        pattern = re.compile(r'^(\+\d{1,3})?(\d{10,12})$')
        if not pattern.match(phone_number):
            raise ValidationError('Invalid phone number')
        return phone_number
