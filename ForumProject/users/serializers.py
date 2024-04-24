from django.core.validators import EmailValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from .models import CustomUser
from .validators import CustomUserValidator


class UserRegisterSerializer(serializers.ModelSerializer):
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
        password = attrs.get('password')
        password2 = attrs.get('password2')
        phone_number = attrs.get('phone_number')

        if password != password2:
            raise serializers.ValidationError("Password fields didn't match.")

        try:
            CustomUserValidator.validate_password(password)
        except ValidationError as error:
            raise serializers.ValidationError(error.detail)

        try:
            CustomUserValidator.validate_phone_number(phone_number)
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
    email = serializers.EmailField(
        validators=[EmailValidator(message="Invalid email")]
    )

    class Meta:
        model = CustomUser
        fields = ['email']


class PasswordResetSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password != password2:
            raise serializers.ValidationError("Password fields didn't match.")

        try:
            CustomUserValidator.validate_password(password)
        except ValidationError as error:
            raise serializers.ValidationError(error.detail)

        return attrs
