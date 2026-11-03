import html
import re
from typing import List, Optional
from bs4 import BeautifulSoup
import httpx
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from core.config import settings
from core.logger import logger
from models.game import Game, MagnetItem


class GameService:
    @staticmethod
    def conv_size_to_bytes(size_str: Optional[str]) -> Optional[int]:
        if not size_str:
            return None

        cleaned = size_str.lower().replace("from", "").strip()

        match = re.search(r"([\d\.]+)\s*([kmgt]?b)", cleaned)
        if not match:
            return None

        value_str, unit = match.groups()
        try:
            value = float(value_str)
        except ValueError:
            return None
        multipliers = {
            "kb": 1024,
            "mb": 1024 ** 2,
            "gb": 1024 ** 3,
            "tb": 1024 ** 4
        }

        multiplier = multipliers.get(unit, 1)
        return int(value * multiplier)




    @staticmethod
    def extract_all_magnets(html_content: str) -> List[MagnetItem]:
        """Extract and clean all magnet links from the HTML content."""
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, "html.parser")
        cleaned_magnets = []
        size = 0
        soup = BeautifulSoup(html_content, "html.parser")
        size_node = soup.find(string=re.compile(r"Repack Size:", re.IGNORECASE))

        h3_tag = soup.find("h3")
        name = h3_tag.get_text(strip=True) if h3_tag else "N/A"

        if size_node:
            strong_tag = size_node.find_next_sibling("strong")
            if strong_tag:
                raw_size = strong_tag.get_text(strip=True)
                size = GameService.conv_size_to_bytes(raw_size)



        for a_tag in soup.find_all("a", href=True):
            href= a_tag.get("href","")
            if href.startswith("magnet:?"):
                decoded = html.unescape(href)
                if decoded not in cleaned_magnets:
                    cleaned_magnets.append(MagnetItem(
                        magnet_link=decoded,
                        size=size,
                        name=name,
                    ))

        return cleaned_magnets

    @staticmethod
    async def sync_database(session: AsyncSession) -> int:
        """Fetch posts from FitGirl and update the database."""
        logger.info("Starting synchronization with the WordPress API...")
        page = 1
        total_synced = 0

        async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}) as client:
            while True:
                logger.debug(f"Fetching page {page}...")
                response = await client.get(settings.WORDPRESS_BASE_URL, params={"per_page": 100, "page": page})

                if response.status_code != 200:
                    logger.warning(
                        f"Pagination ended or received a non-200 response on page {page}: status {response.status_code}")
                    break

                posts = response.json()
                if not posts:
                    break

                for post in posts:
                    content = post["content"]["rendered"]

                    if not GameService.extract_all_magnets(content):
                        continue

                    game = Game(
                        slug=post["slug"],
                        title=post["title"]["rendered"],
                        content=content,
                        date=post["date"]
                    )
                    await session.merge(game)
                    total_synced += 1

                await session.commit()
                page += 1

        logger.success(f"Synchronization completed with {total_synced} items.")
        return total_synced

    @staticmethod
    async def search_games(session: AsyncSession, query: str, limit: int = 20) -> List[Game]:
        """Search games by title or slug."""
        logger.info(f"Search executed for query: '{query}'")
        statement = (
            select(Game)
            .where((Game.title.contains(query)) | (Game.slug.contains(query)))
            .order_by(Game.date.desc())
            .limit(limit)
        )
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def get_game_by_slug(session: AsyncSession, slug: str) -> Optional[Game]:
        logger.info(f"Fetching game with slug: '{slug}'")
        statement = select(Game).where(Game.slug == slug)
        result = await session.exec(statement)
        return result.first()