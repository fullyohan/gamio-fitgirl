import os

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()
class Settings(BaseSettings):
    PROJECT_NAME: str = "FitGirl Provider"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = os.getenv("DB_URL",'')
    SYNC_SECRET_TOKEN: str = os.getenv("SYNC_SECRET_TOKEN",'')
    WORDPRESS_BASE_URL: str = "https://fitgirl-repacks.site/wp-json/wp/v2/posts"

settings = Settings()