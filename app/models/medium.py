from sqlmodel import Field, SQLModel


class Medium(SQLModel, table=True):
    __tablename__ = "media"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)


class MediumCreate(SQLModel):
    name: str


class MediumUpdate(SQLModel):
    name: str


class MediumRead(SQLModel):
    id: int
    name: str
