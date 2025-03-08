import datetime

from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel
from vault.util import generate_uuid, get_utc

if TYPE_CHECKING:
    from vault.util import Checksum


class Document(SQLModel, table=True):
    id: Optional[str] = Field(primary_key=True, default_factory=generate_uuid, description="The document ID")
    fs_path: Optional[str] = Field(description="The path to the document on the filesystem", nullable=False, index=True)

    created_at: datetime.datetime = Field(default=get_utc, description="The time the document was created")

    checksums: Optional[List["Checksum"]] = Relationship(back_populates="document")
