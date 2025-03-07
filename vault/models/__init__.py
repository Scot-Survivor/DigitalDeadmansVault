from vault.models.auth import *
from vault.models.docs import *
from vault.models.util import *

from typing import Any, Generator
from ..config import get_main_config
from sqlmodel import create_engine, Session

config = get_main_config()

engine = create_engine(config.database.url)
SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session
