from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.urls import reverse
from accounts.models import Account, AccountMember, Role
from destinations.models import Destination
from .models import Log
from django.utils.timezone import now

User = get_user_model()
class DataHandlerViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="madhu", password="testpass")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        self.account = Account.objects.create(
            name="Test Account",
            secret_token="secret-token-123",
            created_by=self.user,
            updated_by=self.user
        )

        role = Role.objects.create(role_name="admin")
        AccountMember.objects.create(account=self.account, user=self.user, role=role, created_by=self.user, updated_by=self.user)

        Destination.objects.create(
            account=self.account,
            name="Test Destination",
            url="https://example.com/webhook",
            http_method="POST",
            headers={},
            created_by=self.user,
            updated_by=self.user
        )

        self.url = "/api/server/incoming_data/"

    def test_successful_post(self):
        headers = {
            "HTTP_CL-X-TOKEN": self.account.secret_token,
            "Content-Type": "application/json"
        }
        response = self.client.post(
            self.url,
            data={"event": "signup"},
            format="json",
            **headers
        )
        self.assertEqual(response.status_code, 202)
        self.assertIn("message", response.data)
        self.assertIn("processed_destinations", response.data)

    def test_missing_headers(self):
        response = self.client.post(self.url, data={"event": "signup"}, format="json")
        assert response.status_code == 400

class DestinationViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="madhu", password="testpass")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        self.account = Account.objects.create(name="Test Account", secret_token="secret", created_by=self.user, updated_by=self.user)
        self.role_admin = Role.objects.create(role_name="admin")
        AccountMember.objects.create(account=self.account, user=self.user, role=self.role_admin, created_by=self.user, updated_by=self.user)

        self.destination = Destination.objects.create(
            account=self.account,
            name="Test Destination",
            url="http://example.com/webhook",
            http_method="POST",
            headers={"Content-Type": "application/json"},
            created_by=self.user,
            updated_by=self.user
        )

        self.list_url = reverse('destination-list')
        self.create_url = self.list_url

    def test_list_destinations(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.destination.name)

    def test_create_destination(self):
        payload = {
            "name": "New Destination",
            "url": "https://new.destination/api",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "account": self.account.id
        }
        response = self.client.post(self.create_url, data=payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], payload['name'])

class LogViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="madhu", password="testpass")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.account = Account.objects.create(name="Test Account", secret_token="tok123", created_by=self.user, updated_by=self.user)
        self.role = Role.objects.create(role_name="admin")
        AccountMember.objects.create(account=self.account, user=self.user, role=self.role, created_by=self.user, updated_by=self.user)

        self.destination = Destination.objects.create(
            account=self.account,
            name="Webhook A",
            url="http://example.com",
            http_method="POST",
            headers={},
            created_by=self.user,
            updated_by=self.user
        )

        self.log = Log.objects.create(
            event_id="event123",
            account=self.account,
            destination=self.destination,
            received_data={"event": "signup"},
            status="queued",
            received_timestamp=now(),
            processed_timestamp=now()
        )

        self.url = reverse('log-list')

    def test_list_logs_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['event_id'], self.log.event_id)

    def test_list_logs_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)