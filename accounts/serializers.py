from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Account, AccountMember, Role

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'role_name')


class AccountMemberSerializer(serializers.ModelSerializer):    
    class Meta:
        model = AccountMember
        fields = ['id', 'account', 'user', 'role', 'created_by', 'updated_by']
        read_only_fields = ['created_by', 'updated_by']


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'name', 'secret_token', 'website', 'created_at', 'updated_at', 'created_by', 'updated_by')
        read_only_fields = ('secret_token', 'created_at', 'updated_at', 'created_by', 'updated_by')
