from django.test import TestCase, override_settings
from django.urls import reverse
import json


@override_settings(
    DISCORD_WEBHOOK_URL=None  # So it doesn’t actually call Discord
)
class OCIDiscordWebhookTests(TestCase):

    def setUp(self):
        self.url = reverse('oci_to_discord')
        self.message_payload = {
            "message": "Hello from OCI"
        }

    @override_settings(DISCORD_WEBHOOK_URL=None)
    def test_oci_to_discord_success(self):
        response = self.client.post(
            self.url,
            data=json.dumps(self.message_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "OK"})
