from rest_framework import serializers
from .models import Destination, Log

class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ('id', 'account', 'name', 'url', 'http_method', 'headers')
        read_only_fields = ('account',)

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ('id', 'event_id', 'account', 'destination', 'received_data',
                  'status', 'received_timestamp', 'processed_timestamp', 'error_message')
        read_only_fields = ('account', 'received_timestamp', 'processed_timestamp')
