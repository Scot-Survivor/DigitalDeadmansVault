import os
import random
import shutil
import string
import hashlib
import datetime
import unittest
from fastapi.testclient import TestClient
from vault.main import app
from vault.config import get_main_config


class AbstractTest(unittest.TestCase):
    def setUp(self):
        os.environ['CONFIG_FILE_PATH'] = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'assets/test-config.json'
        )
        os.makedirs("./testing-files", exist_ok=True)
        self.client = TestClient(app)
        self.config = get_main_config()
        self.access_key = self.config.auth.access_key
        self.secret_key = self.config.auth.secret_key
        self.algorithm = str(self.config.auth.hmac_algorithm)

    def tearDown(self):
        self.client = None
        self.config = None
        self.access_key = None
        self.secret_key = None
        self.algorithm = None
        # remove ./testing-files
        shutil.rmtree("./testing-files", ignore_errors=True)

    @staticmethod
    def _calculate_content_md5(content: str) -> str:
        """
        Helper function to calculate the MD5 hash of the content
        :param content:
        :return:
        """
        return hashlib.md5(content.encode()).hexdigest()

    @staticmethod
    def _generate_random_nonce() -> str:
        """
        Helper function to generate a random nonce
        :return: str
        """
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    def _calculate_signature(self, message: str) -> str:
        """
        Helper function to calculate the HMAC signature
        :param message:
        :return:
        """
        return hashlib.new(self.algorithm, message.encode()).hexdigest()

    def _hmac_authentication(self, http_verb, content_type, uri, content) -> dict:
        """
        Helper function to generate the HMAC signature
        :return:
        """
        timestamp = int(datetime.datetime.now().timestamp())
        nonce = self._generate_random_nonce()
        md5 = self._calculate_content_md5(content)
        message = f"{http_verb}\n{md5}\n{content_type}\n{timestamp}\n{uri}\n{nonce}"
        signature = self._calculate_signature(message)
        headers = {
            'Authorization': f'TXC-HMAX-{self.algorithm}: {self.access_key}:{signature}',
            'X-TXC-Nonce': nonce,
            'X-TXC-Timestamp': str(timestamp),
            'Content-MD5': md5,
            'Content-Type': content_type,
        }
        return headers
