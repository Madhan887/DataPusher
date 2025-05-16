from django.db import models
from accounts.models import BaseModel, Account
from django.core.validators import URLValidator

class Destination(BaseModel):
    HTTP_METHOD_CHOICES = (
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
    )
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='destinations')
    name = models.CharField(max_length=255)
    url = models.URLField(validators=[URLValidator()])
    http_method = models.CharField(max_length=5, choices=HTTP_METHOD_CHOICES)
    headers = models.JSONField(default=dict)

    class Meta:
        db_table = 'destinations'
        indexes = [
            models.Index(fields=['account']),
            models.Index(fields=['url']),
        ]

class Log(BaseModel):
    STATUS_CHOICES = (
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    )
    
    event_id = models.CharField(max_length=255, unique=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='logs')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='logs')
    received_data = models.JSONField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    received_timestamp = models.DateTimeField(auto_now_add=True)
    processed_timestamp = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'logs'
        indexes = [
            models.Index(fields=['event_id']),
            models.Index(fields=['status']),
            models.Index(fields=['received_timestamp']),
            models.Index(fields=['processed_timestamp']),
            models.Index(fields=['account', 'destination']),
        ]
