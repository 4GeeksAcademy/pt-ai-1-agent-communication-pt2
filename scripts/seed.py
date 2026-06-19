"""Seed the database with fictional demo data for local development."""

import asyncio

from sqlmodel import select

from app.database import async_session, init_db
from app.models.creator import Creator
from app.models.franchise import Franchise
from app.models.genre import Genre
from app.models.media_item import MediaItem, MediaItemCreatorLink, MediaItemGenreLink
from app.models.medium import Medium


async def seed() -> None:
    await init_db()

    async with async_session() as session:
        existing = await session.execute(select(MediaItem).limit(1))
        if existing.scalar_one_or_none():
            print("Database already seeded — skipping.")
            return

        novel = Medium(name="novel")
        film = Medium(name="film")
        session.add(novel)
        session.add(film)

        fantasy = Genre(name="fantasy")
        scifi = Genre(name="science fiction")
        session.add(fantasy)
        session.add(scifi)

        lotr = Franchise(name="The Lord of the Rings", description="Tolkien's legendarium")
        dune = Franchise(name="Dune", description="Frank Herbert's desert planet saga")
        session.add(lotr)
        session.add(dune)

        tolkien = Creator(name="J.R.R. Tolkien", bio="Author of The Lord of the Rings")
        herbert = Creator(name="Frank Herbert", bio="Author of Dune")
        session.add(tolkien)
        session.add(herbert)

        await session.commit()
        await session.refresh(novel)
        await session.refresh(film)
        await session.refresh(fantasy)
        await session.refresh(scifi)
        await session.refresh(lotr)
        await session.refresh(dune)
        await session.refresh(tolkien)
        await session.refresh(herbert)

        fellowship = MediaItem(
            title="The Fellowship of the Ring",
            description="The first volume of The Lord of the Rings.",
            release_year=1954,
            franchise_id=lotr.id,
            medium_id=novel.id,
        )
        dune_book = MediaItem(
            title="Dune",
            description="A noble family becomes embroiled in war on the desert planet Arrakis.",
            release_year=1965,
            franchise_id=dune.id,
            medium_id=novel.id,
        )
        session.add(fellowship)
        session.add(dune_book)
        await session.commit()
        await session.refresh(fellowship)
        await session.refresh(dune_book)

        session.add(MediaItemCreatorLink(media_item_id=fellowship.id, creator_id=tolkien.id))
        session.add(MediaItemCreatorLink(media_item_id=dune_book.id, creator_id=herbert.id))
        session.add(MediaItemGenreLink(media_item_id=fellowship.id, genre_id=fantasy.id))
        session.add(MediaItemGenreLink(media_item_id=dune_book.id, genre_id=scifi.id))
        await session.commit()

        print("Seed complete.")
        print("  - 2 media items, creators, franchises, genres, media types")
        print("  - First GitHub sign-in becomes admin automatically")


if __name__ == "__main__":
    asyncio.run(seed())
