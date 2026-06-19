from datetime import datetime

from sqlmodel import Field, SQLModel


class ApiKey(SQLModel, table=True):
    __tablename__ = "api_keys"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    key_hash: str = Field(index=True)
    prefix: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    revoked_at: datetime | None = Field(default=None)
