from datetime import datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    github_id: int = Field(unique=True, index=True)
    username: str = Field(index=True)
    display_name: str
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserRead(SQLModel):
    id: int
    username: str
    display_name: str
    is_admin: bool
