from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
import string
import random

def generate_unique_id(length=12, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(length))

def generate_account_id():
    while True:
        account_id = generate_unique_id(12)
        if not User.objects.filter(account_id=account_id).exists():
            break
    return account_id

def generate_chat_id():
    while True:
        chat_id = generate_unique_id(10)
        if not User.objects.filter(chat_id=chat_id).exists():
            break
    return chat_id

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    account_id = models.CharField(max_length=255, unique=True, default=generate_account_id)
    chat_id = models.CharField(max_length=255, unique=True, default=generate_chat_id)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)

    def is_expired(self):
        return timezone.now() > self.expires_at
