import os
import logging

from typing import AnyStr, List
from colorama import Fore, Style
from pydantic import BaseModel
from vault.enums.auth import HMACAlgorithm
from vault.enums.docs import DocumentChecksumAlgorithm


def get_main_config(save_path=None) -> "VaultConfig":
    if save_path is None:
        save_path = os.environ.get("CONFIG_FILE_PATH", "config.json")
    if os.path.exists(save_path):
        return VaultConfig.load(save_path)
    else:
        config = VaultConfig()
        config.save(save_path)
        return config


class Config(BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, path: str | None) -> None:
        """Saves to a yaml file"""
        if path is None:
            path = os.environ.get("CONFIG_FILE_PATH", "config.json")
        with open(path, 'w') as file:
            file.write(self.model_dump_json(indent=4))

    @classmethod
    def load(cls, path: str) -> "Config":
        handle = open(path, 'r')
        model = cls.model_validate_json(handle.read())
        handle.close()
        return model


class AuthConfig(Config):
    """
    Holds all configuration for the authentication
    """

    _has_logged_warning: bool = False
    enabled: bool = True
    secret_key: AnyStr = "my_secret_key"
    access_key: AnyStr = "my_access_key"
    hmac_algorithm: HMACAlgorithm = HMACAlgorithm.SHA256
    nonce_length: int = 16
    nonce_cache_ttl: int = 5  # seconds

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.enabled and not self._has_logged_warning:
            self._has_logged_warning = True
            logging.warning(
                f"{Fore.RED}{Style.BRIGHT}AUTHENTICATION HAS BEEN DISABLED, "
                f"THIS SHOULD ONLY HAPPEN IN DEVELOPMENT{Style.RESET_ALL}"
            )


class DatabaseConfig(Config):
    """
    Holds all configuration for the database
    """

    url: str = "sqlite:///vault.db"


class VaultConfig(Config):
    """
    Holds all configuration for the vault
    """

    base_url: AnyStr = "http://example.com"
    log_level: AnyStr = "INFO"
    file_save_path: AnyStr = "./files"
    database: DatabaseConfig = DatabaseConfig()
    auth: AuthConfig = AuthConfig()
    checksum_algorithms: List[DocumentChecksumAlgorithm] = [
        DocumentChecksumAlgorithm.SHA256,
        DocumentChecksumAlgorithm.MD5,
    ]
