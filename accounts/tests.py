from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.urls import reverse
from accounts.models import Account, AccountMember, Role

User = get_user_model()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

class AuthTests(APITestCase):
    def setUp(self):
        self.username = "Adam"
        self.password = "testpass123"
        self.user = User.objects.create_user(username=self.username, email="adam@gmail.com", password=self.password)

    def test_login_success(self):
        response = self.client.post("/api/accounts/login/", {"username": self.username, "password": self.password})
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)

    def test_login_failure(self):
        response = self.client.post("/api/accounts/login/", {"username": self.username, "password": "wrongpass"})
        self.assertEqual(response.status_code, 400)

    def test_logout(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        response = self.client.post("/api/accounts/logout/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["success"], True)
        self.assertEqual(response.data["message"], "User logged out successfully")


class AccountViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="madhu", password="testpass")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        self.admin_role = Role.objects.create(role_name="admin")

        self.account = Account.objects.create(name="Existing Account", created_by=self.user, updated_by=self.user)
        AccountMember.objects.create(account=self.account, user=self.user, role=self.admin_role, created_by=self.user, updated_by=self.user)

        self.list_url = reverse('account-list')
        self.create_url = self.list_url

    def test_list_accounts(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.account.name)

    def test_create_account(self):
        payload = {
            "name": "New Account"
        }
        response = self.client.post(self.create_url, data=payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], payload['name'])

        new_account_id = response.data['id']
        is_admin = AccountMember.objects.filter(
            account_id=new_account_id,
            user=self.user,
            role__role_name='admin'
        ).exists()
        self.assertTrue(is_admin)

class AccountMemberTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username="admin", email="admin@gamil.com", password="testpass")
        self.normal_user = User.objects.create_user(username="normal", email="normal@gamil.com", password="testpass")

        self.admin_token = Token.objects.create(user=self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        self.account = Account.objects.create(name="Test Account", created_by=self.admin_user, updated_by=self.admin_user)
        self.admin_role = Role.objects.create(role_name="admin")
        self.normal_role = Role.objects.create(role_name="normal")

        AccountMember.objects.create(account=self.account, user=self.admin_user, role=self.admin_role, created_by=self.admin_user, updated_by=self.admin_user)

        self.url = reverse('account-member-create') 

    def test_add_account_member_success(self):
        payload = {
            "account": self.account.id,
            "user": self.normal_user.id,
            "role": "normal"
        }
        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user'], self.normal_user.id)
        self.assertEqual(response.data['role'], self.normal_role.id)

    def test_prevent_duplicate_member(self):
        AccountMember.objects.create(account=self.account, user=self.normal_user, role=self.normal_role, created_by=self.admin_user, updated_by=self.admin_user)

        payload = {
            "account": self.account.id,
            "user": self.normal_user.id,
            "role": "normal"
        }
        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, 400)