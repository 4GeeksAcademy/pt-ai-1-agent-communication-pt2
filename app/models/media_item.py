from sqlmodel import Field, SQLModel
from pydantic import Field as PydanticField


class MediaItemCreatorLink(SQLModel, table=True):
    __tablename__ = "media_item_creators"

    media_item_id: int = Field(foreign_key="media_items.id", primary_key=True)
    creator_id: int = Field(foreign_key="creators.id", primary_key=True)


class MediaItemGenreLink(SQLModel, table=True):
    __tablename__ = "media_item_genres"

    media_item_id: int = Field(foreign_key="media_items.id", primary_key=True)
    genre_id: int = Field(foreign_key="genres.id", primary_key=True)


class MediaItem(SQLModel, table=True):
    __tablename__ = "media_items"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str | None = Field(default=None)
    release_year: int | None = Field(default=None)
    franchise_id: int | None = Field(default=None, foreign_key="franchises.id")
    medium_id: int | None = Field(default=None, foreign_key="media.id")


class MediaItemCreate(SQLModel):
    title: str
    description: str | None = None
    release_year: int | None = None


class MediaItemV1Update(SQLModel):
    title: str
    description: str | None = None
    release_year: int | None = None


class MediaItemV2Create(SQLModel):
    title: str
    description: str | None = None
    release_year: int | None = None
    franchise_id: int | None = None
    medium_id: int


class MediaItemV2Update(SQLModel):
    title: str
    description: str | None = None
    release_year: int | None = None
    franchise_id: int | None = None
    medium_id: int


class MediaItemV1Read(SQLModel):
    id: int
    title: str
    description: str | None = None
    release_year: int | None = None


class MediaItemV2Read(SQLModel):
    id: int
    title: str
    description: str | None = None
    release_year: int | None = None
    franchise_id: int | None = None
    medium_id: int | None = None
    creator_ids: list[int] = PydanticField(default_factory=list)
    genre_ids: list[int] = PydanticField(default_factory=list)


class CreatorLink(SQLModel):
    creator_id: int


class GenreLink(SQLModel):
    genre_id: int
