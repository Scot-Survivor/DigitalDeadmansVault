from ..util import generate_uuid
from typing import List, TYPE_CHECKING, Optional
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .util import Checksum


class Document(SQLModel, table=True):
    id: Optional[str] = Field(primary_key=True, default_factory=generate_uuid, description="The document ID")
    fs_path: Optional[str] = Field(description="The path to the document on the filesystem", nullable=False, index=True)

    checksums: Optional[List["Checksum"]] = Relationship(back_populates="document")
