from django.db import models
import uuid
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

class CustomUserManager(BaseUserManager):
    def create_user(self, phone, password=None, is_active=True, is_staff=False, is_superuser=False, **extra_fields):
        if not phone:
            raise ValueError("Foydalanuvchida telefon raqami bo'lishi shart")
        user = self.model(
            phone=phone,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        return self.create_user(
            phone=phone,
            password=password,
            is_active=True,
            is_staff=True,
            is_superuser=True,
            **extra_fields
        )

class CustomUser(AbstractBaseUser):
    phone = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=20)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()
    USERNAME_FIELD = 'phone'

    def format(self):
        return {
            'phone': self.phone,
            'name': self.name,
            'is_active': self.is_active,
            'is_staff': self.is_staff,
            'is_superuser': self.is_superuser
        }

class OTP(models.Model):
    phone = models.BigIntegerField()
    key = models.CharField(max_length=100, default=lambda: str(uuid.uuid4()))
    code = models.CharField(max_length=4)
    tried = models.IntegerField(default=0)
    is_conf = models.BooleanField(default=False)
    is_expire = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.tried >= 3:
            self.is_expire = True
        super().save(*args, **kwargs)
