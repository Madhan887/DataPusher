from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import UserSerializer, AccountSerializer, AccountMemberSerializer
from .models import Account, AccountMember, Role
from .permissions import IsAccountAdminUser
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.create(user=user)
        return Response({
            'success': True,
            'message': 'User registered successfully',
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'token': token.key
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(ObtainAuthToken):
   
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = response.data.get('token')
        return Response({
            'success': True,
            'token': token
        })


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(members__user=self.request.user)

    def perform_create(self, serializer):
        account = serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )
        role, _ = Role.objects.get_or_create(role_name='admin')
        AccountMember.objects.create(
            account=account,
            user=self.request.user,
            role=role,
            created_by=self.request.user,
            updated_by=self.request.user
        )


class AccountMemberCreateView(generics.CreateAPIView):
    serializer_class = AccountMemberSerializer
    permission_classes = [IsAuthenticated, IsAccountAdminUser]

    def create(self, request, *args, **kwargs):
        role_name = request.data.get('role', 'normal')
        role, _ = Role.objects.get_or_create(role_name=role_name)
        request.data['role'] = role.id

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account = serializer.validated_data['account']
        user = serializer.validated_data['user']

        if AccountMember.objects.filter(account=account, user=user).exists():
            return Response(
                {"error": "This user is already a member of this account"},
                status=status.HTTP_400_BAD_REQUEST
            )

        account_member = AccountMember.objects.create(
            account=account,
            user=user,
            role=role,
            created_by=request.user,
            updated_by=request.user
        )

        return Response(
            AccountMemberSerializer(account_member).data,
            status=status.HTTP_201_CREATED
        )


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.auth.delete()
        return Response({
            'success': True,
            'message': 'User logged out successfully'
        }, status=status.HTTP_200_OK)