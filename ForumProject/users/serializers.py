from django.core.validators import EmailValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from .models import CustomUser, UserRoleCompany, UserStartup
from .validators import CustomUserValidator


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRoleCompany
        fields = ['role']

    def validate_role(self, value):
        if value not in ['startup', 'investor']:
            raise serializers.ValidationError("Role should be a startup or an investor")
        return value


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRoleCompany
        fields = ['company_id']


class BasePasswordSerializer(serializers.ModelSerializer):
    """
    Base serializer for password-related operations.

    This serializer provides a method to validate passwords and their confirmation.

    """
    def validate_passwords(self, password, password2):
        """
        Validates the password and its confirmation.

        Parameters:
        - password (str): The password entered by the user.
        - password2 (str): The confirmation password entered by the user.

        Raises:
        - serializers.ValidationError: If the password and its confirmation do not match,
          or if the password fails the custom validation.

        """
        if password != password2:
            raise serializers.ValidationError({"password2": "Password fields didn't match."})
        try:
            CustomUserValidator.validate_password(password)
        except ValidationError as error:
            raise serializers.ValidationError({"password": error.detail})


class UserRegisterSerializer(BasePasswordSerializer):
    """
    A serializer for user registration.

    This serializer handles user registration data validation and user creation.

    Fields:
    - first_name (str): The first name of the user.
    - last_name (str): The last name of the user.
    - email (str): The email address of the user.
    - password (str): The password of the user.
    - password2 (str): Confirmation of the password.
    - phone_number (str): The phone number of the user.

    Methods:
    - validate: Validates the registration data, ensuring password and phone number are valid.
    - create: Creates a new user instance with the validated registration data.
    """
    first_name = serializers.CharField(required=True, max_length=20)
    last_name = serializers.CharField(required=True, max_length=20)
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    phone_number = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'password2', 'phone_number']

    def validate(self, attrs):
        """
        Validate the registration data.

        Parameters:
        - attrs (dict): A dictionary containing the registration data.

        Returns:
        - dict: A dictionary containing the validated registration data.

        Raises:
        - serializers.ValidationError: If password fields don't match or password/phone number are invalid.
        """
        self.validate_passwords(attrs.get('password'), attrs.get('password2'))

        try:
            CustomUserValidator.validate_phone_number(attrs.get('phone_number'))
        except ValidationError as error:
            raise serializers.ValidationError(error.detail)

        return attrs

    def create(self, validated_data):
        """
        Create a new user instance with the validated registration data.

        Parameters:
        - validated_data (dict): A dictionary containing the validated registration data.

        Returns:
        - (CustomUser): The newly created user instance.
        """
        user = CustomUser.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password']
        )
        return user


class RecoveryEmailSerializer(serializers.ModelSerializer):
    """
    Serializer for handling email addresses during password recovery.

    This serializer validates the email address provided by the user
    during the password recovery process.

    """
    email = serializers.EmailField(
        validators=[EmailValidator(message="Invalid email")]
    )

    class Meta:
        model = CustomUser
        fields = ['email']


class PasswordResetSerializer(BasePasswordSerializer):
    """
    Serializer for resetting the user's password.

    This serializer handles validation of the password reset data.
    It ensures that the password and its confirmation match.
    """
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['password', 'password2']

    def validate(self, attrs):
        """
        Validates the password and its confirmation.

        Parameters:
        - attrs (dict): The dictionary containing password and password2 fields.

        Returns:
        - attrs (dict): The validated dictionary containing password and password2 fields.

        Raises:
        - serializers.ValidationError: If the password and its confirmation do not match.

        """
        self.validate_passwords(attrs.get('password'), attrs.get('password2'))
        return attrs
