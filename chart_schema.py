"""
Astro-Zodiac Chart Schema v1

Single normalized contract shared by:
- Astro Calculation
- House Ruler
- Aspect
- Uranian
- Pattern
- Validation
- AI
- Report

Rule:
Astronomy/astrology engines produce deterministic data.
AI consumes this data and must not recalculate it.
"""

from __future__ import annotations

from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class DMS(BaseModel):
    model_config = ConfigDict(extra="forbid")

    degree_total: float = Field(ge=0, lt=360)
    sign: str
    degree_in_sign: int = Field(ge=0, le=29)
    minute: int = Field(ge=0, le=59)
    second: int = Field(ge=0, le=59)
    dms_str: str


class ChartPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    degree_raw: float = Field(ge=0, lt=360)
    sign: str
    degree_in_sign: int = Field(ge=0, le=29)
    minute: int = Field(ge=0, le=59)
    second: int = Field(ge=0, le=59)
    dms: str
    house: Optional[int] = Field(default=None, ge=1, le=12)
    retrograde: Optional[bool] = None
    point_type: Literal["planet", "angle", "node", "chiron", "uranian"] = "planet"


class HouseCusp(BaseModel):
    model_config = ConfigDict(extra="forbid")

    house: int = Field(ge=1, le=12)
    degree_raw: float = Field(ge=0, lt=360)
    sign: str
    degree_in_sign: int = Field(ge=0, le=29)
    minute: int = Field(ge=0, le=59)
    second: int = Field(ge=0, le=59)
    dms: str


class HouseRuler(BaseModel):
    model_config = ConfigDict(extra="forbid")

    house: int = Field(ge=1, le=12)
    cusp_sign: str
    ruler_planet: str
    ruler_degree_raw: float = Field(ge=0, lt=360)
    ruler_sign: str
    ruler_house: Optional[int] = Field(default=None, ge=1, le=12)
    ruler_dms: str


class Aspect(BaseModel):
    model_config = ConfigDict(extra="forbid")

    p1: str
    p2: str
    aspect: str
    symbol: str
    exact_angle: float
    orb: float = Field(ge=0)
    applying: Optional[bool] = None


class ChartSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    zodiac: str = "tropical"
    house_system: str = "Placidus"
    node_type: str = "mean"
    ephemeris_version: Optional[str] = None


class BirthData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: str
    time: str
    location_name: str
    latitude: float
    longitude: float
    timezone: str = "Asia/Bangkok"
    birth_time_accuracy: Literal["exact", "approximate", "unknown"] = "exact"


class NatalChart(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0"
    birth_data: BirthData
    settings: ChartSettings
    planets: Dict[str, ChartPoint]
    angles: Dict[str, ChartPoint]
    houses: Dict[str, HouseCusp]
    house_rulers: Dict[str, HouseRuler] = {}
    aspects: List[Aspect] = []


class TransitPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    degree_raw: float = Field(ge=0, lt=360)
    sign: str
    dms: str
    timestamp_utc: str


class NormalizedChart(BaseModel):
    """
    Canonical object passed between Astrology -> Evidence -> Pattern -> AI.
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0"
    natal: NatalChart
    transits: Dict[str, TransitPoint] = {}
