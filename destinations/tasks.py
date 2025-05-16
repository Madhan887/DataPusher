import json
import requests
from celery import shared_task
from django.utils import timezone
from .models import Log, Destination
from urllib.parse import urlencode

@shared_task
def push_data_to_destination(log_id):
    log = Log.objects.get(id=log_id)
    destination = log.destination
    
    try:
        headers = destination.headers
        data = log.received_data
        
        if destination.http_method == 'GET':
            url = f"{destination.url}?{urlencode(data)}"
            response = requests.get(url, headers=headers)
        else:
            url = destination.url
            response = requests.request(
                method=destination.http_method,
                url=url,
                json=data,
                headers=headers
            )
        
        success = 200 <= response.status_code < 300
        log.status = 'success' if success else 'failed'
        log.error_message = None if success else response.text
        
    except Exception as e:
        log.status = 'failed'
        log.error_message = str(e)
    
    log.processed_timestamp = timezone.now()
    log.save()