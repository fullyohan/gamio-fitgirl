from sqlmodel import SQLModel, Field

# Database entity
class Game(SQLModel, table=True):
    __tablename__ = "games"

    slug: str = Field(primary_key=True, index=True)
    title: str = Field(index=True)
    content: str
    date: str

# Pydantic DTOs for API responses
class GameSearchItem(SQLModel):
    slug: str
    title: str
    date: str

class MagnetItem(SQLModel):
    name: str
    magnet_link:str
    size:int
    seeders: int = 0

