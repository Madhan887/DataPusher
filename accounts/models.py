from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string
from django.core.validators import URLValidator

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='%(class)s_created')
    updated_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='%(class)s_updated')

    class Meta:
        abstract = True

class User(AbstractUser):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='created_users')
    updated_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='updated_users')

class Account(BaseModel):
    name = models.CharField(max_length=255)
    secret_token = models.CharField(max_length=64, unique=True, editable=False)
    website = models.URLField(blank=True, null=True, validators=[URLValidator()])

    def save(self, *args, **kwargs):
        if not self.secret_token:
            self.secret_token = get_random_string(64)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'accounts'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['secret_token']),
        ]

class Role(BaseModel):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('normal', 'Normal User')
    )
    role_name = models.CharField(max_length=10, choices=ROLE_CHOICES)

    class Meta:
        db_table = 'roles'

class AccountMember(BaseModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        db_table = 'account_members'
        unique_together = ('account', 'user')
        indexes = [
            models.Index(fields=['account', 'user']),
            models.Index(fields=['role']),
        ]
