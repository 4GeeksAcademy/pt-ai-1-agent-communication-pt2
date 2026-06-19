from sqlmodel import Field, SQLModel


class Franchise(SQLModel, table=True):
    __tablename__ = "franchises"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str | None = Field(default=None)


class FranchiseCreate(SQLModel):
    name: str
    description: str | None = None


class FranchiseUpdate(SQLModel):
    name: str
    description: str | None = None


class FranchiseRead(SQLModel):
    id: int
    name: str
    description: str | None = None
