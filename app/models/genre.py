from sqlmodel import Field, SQLModel


class Genre(SQLModel, table=True):
    __tablename__ = "genres"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)


class GenreCreate(SQLModel):
    name: str


class GenreUpdate(SQLModel):
    name: str


class GenreRead(SQLModel):
    id: int
    name: str
