from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DataHandlerView, DestinationViewSet, LogViewSet

router = DefaultRouter()
router.register(r'destinations', DestinationViewSet, basename='destination')
router.register(r'logs', LogViewSet, basename='log')

urlpatterns = [
    path('server/incoming_data/', DataHandlerView.as_view(), name='incoming-data'),
    path('', include(router.urls)),
]
