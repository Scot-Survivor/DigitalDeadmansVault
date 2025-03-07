import os
import abc
import uuid
import string
import random

from abc import abstractmethod
from typing import Union, AnyStr, Any
from vault.config import get_main_config

BytesLike = Union[bytes, bytearray, memoryview]

config = get_main_config()


def generate_uuid():
    return str(uuid.uuid4())


def get_extension(filename: AnyStr):
    return os.path.splitext(filename)[-1]


def generate_random_filename(extension: AnyStr):
    random_filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    return f"{random_filename}{extension}"


async def save_a_file(file: BytesLike, filename: AnyStr) -> AnyStr:
    save_path = os.path.join(os.getcwd(), config.file_save_path)
    save_path = os.path.join(save_path, generate_random_filename(get_extension(filename)))
    with open(save_path, "wb") as f:
        f.write(file)
    return save_path
