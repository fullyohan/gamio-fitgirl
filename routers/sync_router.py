from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import APIKeyQuery, HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from core.config import settings
from core.logger import logger
from db.database import get_session
from services.game_service import GameService

router = APIRouter(prefix="/sync", tags=["Admin / Sync"])
api_key_query = APIKeyQuery(name="token", auto_error=False)

security = HTTPBearer()


@router.post("")
async def trigger_sync(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: AsyncSession = Depends(get_session)
):
    token = credentials.credentials

    if token != settings.SYNC_SECRET_TOKEN:
        logger.warning("Unauthorized access attempt to the /sync route")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing access token."
        )

    try:
        count = await GameService.sync_database(session=session)
        return {"status": "success", "message": f"Successfully synchronized {count} repacks."}
    except Exception as e:
        logger.error(f"Synchronization failed: {e}")
        raise HTTPException(status_code=500, detail="Internal synchronization error.")