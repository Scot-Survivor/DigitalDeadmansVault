import hashlib
from vault.enums.internal import SerializableEnum


class DocumentChecksumAlgorithm(SerializableEnum):
    MD5 = "md5"
    SHA256 = "sha256"
    SHA512 = "sha512"

    def hash(self, message: str) -> str:
        return str(hashlib.new(self.value, message.encode()).hexdigest())

    @staticmethod
    def from_header_str(header_string: str):
        """
        Get the algorithm from the header string
            "  TXC-HMAX-ALGORITHM: <ACCESS_KEY>:<SIGNATURE>"
        :param header_string:
        :return:
        """
        algorithm = header_string.split(" ")[0].strip().split("-")[-1][:-1]
        return DocumentChecksumAlgorithm(algorithm.lower())

    def __str__(self):
        return self.value
