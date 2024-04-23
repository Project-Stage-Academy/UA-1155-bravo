from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, password.

        Parameters:
        - email (str): The email address of the user.
        - password (str): The password of the user.
        - **extra_fields(dict): Other information.

        Returns:
        - CustomUser: The newly created user instance.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a superuser with the given email and password.

        Parameters:
        - email (str): The email address of the user.
        - password (str): The password of the user.
        - **extra_fields(dict): Other information.

        Returns:
        - CustomUser: The newly created user instance.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    A custom user model for authentication.

    This model represents a user in the system, using email as the unique identifier.

    Fields:
    - id (BigAutoField): The primary key of the user.
    - first_name (CharField): The first name of the user.
    - last_name (CharField): The last name of the user.
    - email (EmailField): The email address of the user (unique).
    - phone_number (CharField): The phone number of the user.
    - is_active (BooleanField): A flag indicating whether the user account is active.
    - is_staff (BooleanField): A flag indicating whether the user has staff access.
    - is_superuser (BooleanField): A flag indicating whether the user is a superuser.

    Manager:
    - objects: The default manager for the CustomUser model.

    Attributes:
    - USERNAME_FIELD: The field used as the unique identifier for authentication.
    - REQUIRED_FIELDS: The list of fields required when creating a user.

    Methods:
    - __str__: Return a string representation of the user.
    """
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']
    objects = CustomUserManager()

    def __str__(self):
        """
        Return a string representation of the user.

        Returns:
        - str: The string representation of the user.
        """
        return self.email
