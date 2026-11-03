import json
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
load_dotenv()
from core.config import settings
from core.logger import logger
from db.database import engine, init_db
from routers import game_router, sync_router
from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} (v{settings.VERSION})...")
    await init_db()
    try:
        yield
    finally:
        logger.info(f"{settings.PROJECT_NAME} shutdown.")
        await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.include_router(game_router.router)
app.include_router(sync_router.router)
app.mount("/assets", StaticFiles(directory="assets"), name="assets")


@app.get("/manifest.json")
def get_manifest():
    file_path = "manifest.json"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Manifest file not found.")

    with open(file_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    manifest_data["icon"] = f"{os.getenv('URL')}/assets/icon.png"

    return manifest_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)