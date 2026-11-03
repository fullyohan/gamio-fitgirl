from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from db.database import get_session
from models.game import GameSearchItem, MagnetItem
from services.game_service import GameService

router = APIRouter(prefix="", tags=["Games"])

@router.get("/search", response_model=List[GameSearchItem])
async def search_games(
        q: str = Query(..., min_length=2, description="Game title or slug"),
        session: AsyncSession = Depends(get_session)
):
    games = await GameService.search_games(session, query=q)
    return [GameSearchItem(slug=g.slug, title=g.title, date=g.date) for g in games]


@router.get("/magnets/{slug}", response_model=List[MagnetItem])
async def get_game_by_slug(
        slug: str,
        session: AsyncSession = Depends(get_session)
):
    game = await GameService.get_game_by_slug(session, slug=slug)
    if not game:
        raise HTTPException(status_code=404, detail="No game found for this slug.")

    magnets = GameService.extract_all_magnets(game.content)

    return magnets