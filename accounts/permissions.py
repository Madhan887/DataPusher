from rest_framework import permissions
from accounts.models import AccountMember

class IsAccountAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        account = self._get_account_from_view(view, request)
        
        if not account:
            return False

        return AccountMember.objects.filter(
            user=request.user,
            account=account,
            role__role_name='admin'
        ).exists()

    def has_object_permission(self, request, view, obj):
        account = getattr(obj, 'account', None)
        if not account:
            return False

        return AccountMember.objects.filter(
            user=request.user,
            account=account,
            role__role_name='admin'
        ).exists()

    def _get_account_from_view(self, view, request):
        if hasattr(view, 'get_object') and hasattr(view, 'action') and view.action in ['retrieve', 'update', 'destroy']:
            try:
                obj = view.get_object()
                return getattr(obj, 'account', None)
            except:
                return None
        if hasattr(request.user, 'accountmember_set'):
            return request.user.accountmember_set.first().account
        return None


class IsAccountMemberUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        account = self._get_account_from_view(view, request)
        if not account:
            return False

        return AccountMember.objects.filter(
            user=request.user,
            account=account
        ).exists()

    def has_object_permission(self, request, view, obj):
        account = getattr(obj, 'account', None)
        if not account:
            return False

        return AccountMember.objects.filter(
            user=request.user,
            account=account
        ).exists()

    def _get_account_from_view(self, view, request):
        if hasattr(view, 'get_object'):
            try:
                obj = view.get_object()
                return getattr(obj, 'account', None)
            except:
                return None
        if hasattr(request.user, 'accountmember_set'):
            return request.user.accountmember_set.first().account
        return None
