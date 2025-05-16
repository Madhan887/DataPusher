from celery import shared_task
from django.utils import timezone
import requests
from .models import Log

@shared_task
def process_destination_data(log_id):
    log = Log.objects.get(id=log_id)
    destination = log.destination
    
    try:
        # Prepare data based on HTTP method
        if destination.http_method == 'GET':
            response = requests.get(destination.url, params=log.data, headers=destination.headers)
        else:  # POST or PUT
            method = requests.post if destination.http_method == 'POST' else requests.put
            response = method(destination.url, json=log.data, headers=destination.headers)
        
        # Update log status
        log.status = 'success' if response.ok else 'failed'
        log.error_message = None if response.ok else response.text
        
    except Exception as e:
        log.status = 'failed'
        log.error_message = str(e)
    
    log.processed_timestamp = timezone.now()
    log.save()