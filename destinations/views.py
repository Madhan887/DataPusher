from django.core.cache import cache
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.throttling import SimpleRateThrottle
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from accounts.models import Account, AccountMember
from .models import Destination, Log
from .serializers import DestinationSerializer, LogSerializer
from .tasks import push_data_to_destination
from accounts.permissions import IsAccountAdminUser
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError
import uuid



class AccountRateThrottle(SimpleRateThrottle):
    rate = '5/second'

    def get_cache_key(self, request, view):
        token = request.headers.get('CL-X-TOKEN')
        if not token:
            return None
        return token

class DataHandlerView(APIView):
    authentication_classes = [TokenAuthentication]
    throttle_classes = [AccountRateThrottle]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('CL-X-TOKEN', openapi.IN_HEADER, type=openapi.TYPE_STRING, required=True)
        ],
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT),
        responses={
            202: "Data received and queued",
            400: "Invalid request or duplicate event",
            401: "Authentication failed",
            429: "Rate limit exceeded"
        }
    )
    def post(self, request):
        token = request.headers.get('CL-X-TOKEN')
        
        if not token:
            return Response({'error': 'Missing token header'}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(request.data, dict):
            return Response({'error': 'Invalid data format'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = Account.objects.get(secret_token=token)
        except Account.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
       
        destinations = Destination.objects.filter(account=account)
        logs = [
            Log(event_id=str(uuid.uuid4()), account=account, destination=d, received_data=request.data)
            for d in destinations
        ]
        
        try:
            created_logs = Log.objects.bulk_create(logs)
            for log in created_logs:
                push_data_to_destination.delay(log.id)
            return Response(
                {'message': 'Queued', 'processed_destinations': len(created_logs)},
                status=status.HTTP_202_ACCEPTED
            )
        except IntegrityError:
            return Response(
                {'error': 'Event processing conflict'}, 
                status=status.HTTP_409_CONFLICT
            )


class DestinationViewSet(viewsets.ModelViewSet):
    serializer_class = DestinationSerializer
    permission_classes = [IsAuthenticated, IsAccountAdminUser]

    def get_queryset(self):
        cache_key = f'dest_{self.request.user.id}'
        queryset = cache.get(cache_key)
        if not queryset:
            queryset = Destination.objects.filter(account__members__user=self.request.user)
            cache.set(cache_key, queryset, 300)
        return queryset

    def perform_create(self, serializer):
        account_id = self.request.data.get("account")
        
        if not account_id:
            raise ValidationError("Account ID is required.")

        try:
            account = Account.objects.get(id=account_id)
        except Account.DoesNotExist:
            raise ValidationError("Account not found.")

        if not AccountMember.objects.filter(user=self.request.user, account=account).exists():
            raise PermissionDenied("You are not a member of this account.")

        serializer.save(account=account, created_by=self.request.user, updated_by=self.request.user)
        cache.delete(f'dest_{self.request.user.id}')

    def perform_update(self, serializer):
        serializer.save()
        cache.delete(f'dest_{self.request.user.id}')

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete(f'dest_{self.request.user.id}')

class LogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LogSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cache_key = self._get_cache_key()
        queryset = cache.get(cache_key)
        if not queryset:
            queryset = Log.objects.filter(account__members__user=self.request.user)
            filters = {}

            for param in ['destination_id', 'status']:
                if value := self.request.query_params.get(param):
                    filters[param] = value

            for param in ['received_timestamp', 'processed_timestamp']:
                if value := self.request.query_params.get(param):
                    filters[f'{param}__date'] = value

            if filters:
                queryset = queryset.filter(**filters)
            cache.set(cache_key, queryset, 60)
        return queryset

    def _get_cache_key(self):
        params = self.request.query_params.copy()
        params['user_id'] = self.request.user.id
        return f"log_{hash(frozenset(params.items()))}"
