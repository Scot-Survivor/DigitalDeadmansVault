import hashlib
import os.path
import mimetypes
from tests.internal import AbstractTest


class DocumentTests(AbstractTest):
    def _generate_random_hash(self) -> str:
        return hashlib.md5(self._generate_random_nonce().encode()).hexdigest()

    @staticmethod
    def _build_file_body(file_path: str, boundary: str) -> str:
        handle = open(file_path, "rb")
        # get the type of the file for the content-type
        content_type = mimetypes.guess_type(file_path)[0]
        file_name = os.path.basename(file_path)
        return (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{file_name}\"\r\n"
            f"Content-Type: {content_type}\r\n\r\n{handle.read().decode()}\r\n--{boundary}--\r\n"
        )

    def test_document_creation(self):
        """
        Test the creation of a document, and the checksums associated with it
        multipart/form-data
        :return:
        """
        # handle = open("./assets/test.txt", "rb")
        boundary = self._generate_random_hash()
        body = self._build_file_body("./tests/assets/test.txt", boundary)
        content_type = f"multipart/form-data; boundary={boundary}"
        headers = self._hmac_authentication("POST", content_type, "/docs/create", body)

        response = self.client.post("/docs/create", data=body, headers=headers)
        self.assertTrue(response.status_code == 200, f"Response: {response.json()}")
