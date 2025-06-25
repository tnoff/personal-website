from django.test import TestCase, override_settings
from django.urls import reverse
from base64 import b64encode
from homepage.views import check_authorization
import json
import os


@override_settings(
    OCI_WEBHOOK_USER='testuser',
    OCI_WEBHOOK_PASS='testpass',
    DISCORD_WEBHOOK_URL=None  # So it doesn’t actually call Discord
)
class OCIDiscordWebhookTests(TestCase):

    def setUp(self):
        self.url = reverse('oci_to_discord')
        self.message_payload = {
            "message": "Hello from OCI"
        }
        self.username = "testuser"
        self.password = "testpass"

    def _make_auth_header(self, username, password):
        credentials = f"{username}:{password}"
        encoded = b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def test_check_authorization_valid(self):
        headers = {
            'Authorization': self._make_auth_header(self.username, self.password)
        }
        self.assertTrue(check_authorization(headers))

    def test_check_authorization_invalid(self):
        headers = {
            'Authorization': self._make_auth_header("wrong", "credentials")
        }
        self.assertFalse(check_authorization(headers))

    def test_check_authorization_missing(self):
        self.assertFalse(check_authorization({}))

    @override_settings(DISCORD_WEBHOOK_URL=None)
    def test_oci_to_discord_success(self):
        auth_header = self._make_auth_header(self.username, self.password)
        response = self.client.post(
            self.url,
            data=json.dumps(self.message_payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=auth_header
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "OK"})

    def test_oci_to_discord_unauthorized(self):
        response = self.client.post(
            self.url,
            data=json.dumps(self.message_payload),
            content_type="application/json"
            # No auth header
        )
        self.assertEqual(response.status_code, 401)
