from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from investors.models import Investor
from startups.models import Startup


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
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
        Create and save a SuperUser with the given email and password.
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
    Custom user model representing a user of the application.

    Attributes:
        id (int): The unique identifier for the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        email (str): The email address of the user.
        phone_number (str): The phone number of the user.
        is_active (bool): Indicates whether the user account is active.
        is_staff (bool): Indicates whether the user has staff-level access.
        is_superuser (bool): Indicates whether the user has superuser privileges.
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
        Returns a string representation of the user.

        Returns:
            str: The email address of the user.
        """
        return self.email


class UserInvestor(models.Model):
    """
    Represents the relationship between a user and an investor.

    Attributes:
        customuser (CustomUser): The user associated with the investor.
        investor (Investor): The investor associated with the user.
        investor_role_id (int): The role ID of the user within the investor organization.
    """

    customuser = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE)
    investor_role_id = models.IntegerField()


class UserStartup(models.Model):
    """
    Represents the relationship between a user and a startup.

    Attributes:
        customuser (CustomUser): The user associated with the startup.
        startup (Startup): The startup associated with the user.
        startup_role_id (int): The role ID of the user within the startup organization.
    """

    customuser = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE)
    startup_role_id = models.IntegerField()
