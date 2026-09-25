from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field

class HouseLordItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    key: str
    lord_house: int = Field(ge=1, le=12)
    destination_house: int = Field(ge=1, le=12)
    title: str
    bullets: list[str]

class HouseLordSearchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    total: int = Field(ge=0)
    items: list[HouseLordItem]
