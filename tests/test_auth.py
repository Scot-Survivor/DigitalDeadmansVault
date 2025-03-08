import hashlib
import datetime
from tests.internal import AbstractTest
from vault.models.auth import HMACObject


class TestAuth(AbstractTest):

    def _calculate_signature(self, message: str) -> str:
        hmac_obj = HMACObject(key=self.secret_key, message=message, algorithm=self.algorithm)
        return hmac_obj.signature

    def test_failed_auth(self):
        response = self.client.get("/auth/protected")
        self.assertFalse(response.status_code == 200)
        self.assertTrue(response.status_code == 403)

    def test_accurate_auth(self):
        body = ""
        md5 = hashlib.md5(body.encode()).hexdigest()
        nonce = "1234567890"
        timestamp = int(datetime.datetime.now().timestamp())
        message = f"GET\n{md5}\napplication/json\n{timestamp}\n/auth/protected\n{nonce}"
        signature = self._calculate_signature(message)
        headers = {
            "Authorization": f"TXC-HMAX-SHA256: {self.access_key}:{signature}",
            "X-TXC-Nonce": nonce,
            "X-TXC-Timestamp": str(timestamp),
            "Content-MD5": md5,
            "Content-Type": "application/json",
        }
        response = self.client.get("/auth/protected", headers=headers)
        self.assertTrue(response.status_code == 200, f"Response: {response.json()}")
        self.assertTrue(response.json()["access_key"] == self.access_key)
