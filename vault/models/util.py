from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from vault.docs import Document


class Checksum(SQLModel, table=True):
    id: int = Field(primary_key=True, description="The checksum ID")
    value: str = Field(description="The checksum value", nullable=False)
    algorithm: str = Field(description="The checksum algorithm", nullable=False)

    document_id: str = Field(description="The document ID", foreign_key="document.id", nullable=False)
    document: Optional["Document"] = Relationship(back_populates="checksums")
