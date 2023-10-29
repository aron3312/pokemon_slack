from typing import List, Optional

from pydantic import BaseModel, PositiveInt


class Base(BaseModel):
    class Config:
        orm_mode = True


class Player(Base):
    name: str


class PlayerCreate(Player):
    name: str
    text: Optional[int] = None
