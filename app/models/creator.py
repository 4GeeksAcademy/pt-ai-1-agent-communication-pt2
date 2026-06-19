from sqlmodel import Field, SQLModel


class Creator(SQLModel, table=True):
    __tablename__ = "creators"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    bio: str | None = Field(default=None)


class CreatorCreate(SQLModel):
    name: str
    bio: str | None = None


class CreatorUpdate(SQLModel):
    name: str
    bio: str | None = None


class CreatorRead(SQLModel):
    id: int
    name: str
    bio: str | None = None
