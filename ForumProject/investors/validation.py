from django.core.validators import RegexValidator, FileExtensionValidator


phone_regex = RegexValidator(
    regex=r'^\+1?\d{9,15}$',
    message="The phone number must be in the format: '+1234567890'. The Minimum length 9 Maximum length 15 digits."
)

image_validator = FileExtensionValidator(
    allowed_extensions=['jpg', 'jpeg', 'png', 'gif'],
    message="Only files with extensions: jpg, jpeg, png, gif are allowed."
)

"""
Validators for phone numbers and image files.

Attributes:
    phone_regex (RegexValidator): Validator for phone numbers.
    image_validator (FileExtensionValidator): Validator for image files.

These validators ensure that phone numbers and image files meet specified criteria.
"""