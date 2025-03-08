import hashlib
import logging
import datetime
import cachetools

from fastapi import HTTPException, Request
from fastapi.security.http import HTTPBase
from fastapi.openapi.models import HTTPBase as HTTPBaseModel
from vault.config import get_main_config
from vault.enums.auth import HMACAlgorithm
from vault.models.auth import HMACObject

config = get_main_config()


# noinspection PyMissingConstructor
class HMACAuth(HTTPBase):
    def __init__(self, *, scheme_name: str = None, description: str = None, auto_error: bool = True):
        self.model = HTTPBaseModel(scheme="hmac", description=description)
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error
        self.nonce_cache = cachetools.TTLCache(maxsize=config.auth.nonce_cache_ttl, ttl=config.auth.nonce_cache_ttl)
        self.ttl = config.auth.nonce_cache_ttl
        self.exception = HTTPException(403, "Not authenticated")

    def _validate_nonce(self, nonce: str) -> bool:
        """Validate the nonce"""
        if self.nonce_cache.get(nonce):
            return False
        self.nonce_cache[nonce] = True
        return True

    def _validate_headers(self, request: Request):
        """Ensure all headers needed are present"""
        headers = ["Authorization", "X-TXC-Nonce", "X-TXC-Timestamp", "Content-MD5", "Content-Type"]
        if not all(header in request.headers for header in headers):
            logging.debug("Missing headers for HMAC authentication")
            raise self.exception

    async def _validate_md5(self, request: Request):
        """Validate the MD5 hash"""
        content_md5 = request.headers.get("Content-MD5").strip()
        if content_md5 != "":
            body = await request.body()
            md5 = hashlib.md5(body).hexdigest()
            if md5 != content_md5:
                logging.debug("Invalid MD5 hash")
                if self.auto_error:
                    raise self.exception

    def _validate_signature(
        self,
        request: Request,
        access_key: str,
        signature: str,
        nonce: str,
        timestamp: datetime.datetime,
        content_md5: str,
        algorithm: HMACAlgorithm,
        content_type: str,
    ) -> None:
        """Validate the signature"""
        if algorithm != config.auth.hmac_algorithm:
            logging.debug("Invalid algorithm")
            if self.auto_error:
                raise self.exception

        if access_key != config.auth.access_key:
            logging.debug("Invalid access key")
            if self.auto_error:
                raise self.exception

        if not self._validate_nonce(nonce):
            logging.debug("Invalid nonce")
            if self.auto_error:
                raise self.exception

        uri = request.url.path
        message = f"{request.method}\n{content_md5}\n{content_type}\n{int(timestamp.timestamp())}\n{uri}\n{nonce}"
        logging.debug(f"Message: {message}")
        hmac_obj = HMACObject(key=config.auth.secret_key, message=message, algorithm=algorithm)
        logging.debug(f"Calculated signature: {hmac_obj.signature}")
        if hmac_obj.signature != signature:
            logging.debug("Invalid signature")
            if self.auto_error:
                raise self.exception

    async def __call__(self, request: Request) -> str | None:  # will return access_key
        self._validate_headers(request)
        # breakpoint()
        await self._validate_md5(request)
        auth_header = request.headers.get("Authorization").strip()
        nonce = request.headers.get("X-TXC-Nonce").strip()
        timestamp = datetime.datetime.fromtimestamp(
            int(request.headers.get("X-TXC-Timestamp").strip()), tz=datetime.timezone.utc
        )
        header_parts = auth_header.split(":")
        access_key = header_parts[1].strip()
        signature = header_parts[2].strip()
        algorithm = HMACAlgorithm.from_header_str(auth_header)
        content_md5 = request.headers.get("Content-MD5").strip()
        content_type = request.headers.get("Content-Type").strip()
        self._validate_signature(request, access_key, signature, nonce, timestamp, content_md5, algorithm, content_type)
        return access_key
