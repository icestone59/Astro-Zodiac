"""
Astro-Zodiac — T2 Astro Calculation Engine

Purpose:
- Calculate natal chart with Swiss Ephemeris.
- Return the canonical NormalizedChart schema.
- Preserve a small legacy-compatible entry point during migration.

Important:
- This module performs deterministic astrology calculations.
- AI does not calculate chart positions.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path as FilePath
from typing import Dict, Optional, Tuple

import swisseph as swe

# Prefer the project's bundled Swiss Ephemeris files.
# This keeps Render/local execution independent of the host's global swe path.
PROJECT_EPHE_PATH = FilePath(__file__).resolve().parent / "ephe"
if PROJECT_EPHE_PATH.is_dir():
    swe.set_ephe_path(str(PROJECT_EPHE_PATH))

from chart_schema import (
    BirthData,
    ChartPoint,
    ChartSettings,
    HouseCusp,
    NatalChart,
    NormalizedChart,
)

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Existing MVP location catalogue.
# Unknown locations are intentionally handled by a fallback for compatibility;
# geocoding will be hardened in a later phase.
LOCATION_COORDS = {
    "กรุงเทพมหานคร": (13.7563, 100.5018),
    "เชียงใหม่": (18.7883, 98.9853),
    "ขอนแก่น": (16.4322, 102.8236),
    "ชลบุรี": (13.3611, 100.9847),
    "สงขลา": (7.1988, 100.5951),
    "นครราชสีมา": (14.9799, 102.0978),
    "ภูเก็ต": (7.8804, 98.3923),
    "นนทบุรี": (13.8591, 100.5217),
    "ปทุมธานี": (14.0208, 100.5250),
    "สมุทรปราการ": (13.5991, 100.5998),
}

# Swiss Ephemeris planetary factors used by the existing project.
PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
    "Chiron": swe.CHIRON,
    "NorthNode": swe.MEAN_NODE,
    "Cupido": swe.CUPIDO,
    "Hades": swe.HADES,
    "Zeus": swe.ZEUS,
    "Kronos": swe.KRONOS,
    "Apollon": swe.APOLLON,
    "Admetos": swe.ADMETOS,
    "Vulkanus": swe.VULKANUS,
    "Poseidon": swe.POSEIDON,
}

PLANET_POINT_TYPES = {
    "Chiron": "chiron",
    "NorthNode": "node",
    "Cupido": "uranian",
    "Hades": "uranian",
    "Zeus": "uranian",
    "Kronos": "uranian",
    "Apollon": "uranian",
    "Admetos": "uranian",
    "Vulkanus": "uranian",
    "Poseidon": "uranian",
}


def get_coordinates(location_name: str) -> Tuple[float, float]:
    """Return (latitude, longitude) for a known location."""
    return LOCATION_COORDS.get(location_name, LOCATION_COORDS["กรุงเทพมหานคร"])


def deg_to_dms(deg_float: float) -> dict:
    """Convert absolute ecliptic longitude to canonical sign/DMS components."""
    degree_total = float(deg_float) % 360.0
    whole_degree = int(degree_total)
    minute_float = (degree_total - whole_degree) * 60.0
    minute = int(minute_float)
    second = int(round((minute_float - minute) * 60.0))

    # Handle rounding like 29°59'60".
    if second == 60:
        second = 0
        minute += 1
    if minute == 60:
        minute = 0
        whole_degree += 1
        degree_total = float(whole_degree % 360)

    sign_idx = int(degree_total // 30) % 12
    degree_in_sign = int(degree_total % 30)

    return {
        "degree_total": round(degree_total, 6),
        "sign": ZODIAC_SIGNS[sign_idx],
        "degree_in_sign": degree_in_sign,
        "minute": minute,
        "second": second,
        "dms_str": f"{degree_in_sign}°{ZODIAC_SIGNS[sign_idx]} {minute}'{second}\"",
    }


def _point_type(name: str) -> str:
    if name == "Chiron":
        return "chiron"
    if name == "NorthNode":
        return "node"
    if name in PLANET_POINT_TYPES:
        return PLANET_POINT_TYPES[name]
    return "planet"


def _calc_point(name: str, planet_id: int, julian_day: float) -> ChartPoint:
    result, _flag = swe.calc_ut(julian_day, planet_id)
    degree = float(result[0]) % 360.0
    speed_longitude = float(result[3])
    dms = deg_to_dms(degree)

    return ChartPoint(
        name=name,
        degree_raw=round(degree, 6),
        sign=dms["sign"],
        degree_in_sign=dms["degree_in_sign"],
        minute=dms["minute"],
        second=dms["second"],
        dms=dms["dms_str"],
        house=None,
        retrograde=speed_longitude < 0,
        point_type=_point_type(name),
    )


def _assign_house(longitude: float, cusps: Tuple[float, ...]) -> int:
    """
    Assign ecliptic longitude to one of 12 Placidus houses.

    cusps is expected to contain 12 values indexed 0..11.
    Each house starts at cusp[i] and ends at cusp[(i+1) % 12].
    """
    lon = float(longitude) % 360.0
    normalized = [float(c) % 360.0 for c in cusps]

    for idx in range(12):
        start = normalized[idx]
        end = normalized[(idx + 1) % 12]

        if start <= end:
            inside = start <= lon < end
        else:
            inside = lon >= start or lon < end

        if inside:
            return idx + 1

    # Numerical edge case: exactly on a cusp.
    closest_idx = min(
        range(12),
        key=lambda i: min(
            (lon - normalized[i]) % 360.0,
            (normalized[i] - lon) % 360.0,
        ),
    )
    return closest_idx + 1


def _build_house_cusps(cusps: Tuple[float, ...]) -> Dict[str, HouseCusp]:
    houses: Dict[str, HouseCusp] = {}
    for index, cusp in enumerate(cusps[:12], start=1):
        degree = float(cusp) % 360.0
        dms = deg_to_dms(degree)
        houses[f"House_{index}"] = HouseCusp(
            house=index,
            degree_raw=round(degree, 6),
            sign=dms["sign"],
            degree_in_sign=dms["degree_in_sign"],
            minute=dms["minute"],
            second=dms["second"],
            dms=dms["dms_str"],
        )
    return houses


def _make_angles(asc_deg: float, mc_deg: float) -> Dict[str, ChartPoint]:
    result: Dict[str, ChartPoint] = {}
    for name, degree in (("ASC", asc_deg), ("MC", mc_deg)):
        dms = deg_to_dms(degree)
        result[name] = ChartPoint(
            name=name,
            degree_raw=round(float(degree) % 360.0, 6),
            sign=dms["sign"],
            degree_in_sign=dms["degree_in_sign"],
            minute=dms["minute"],
            second=dms["second"],
            dms=dms["dms_str"],
            house=None,
            retrograde=False,
            point_type="angle",
        )
    return result


def _resolve_birth_datetime(
    day: int,
    month: int,
    year: int,
    hour: int,
    minute: int,
    timezone_offset_hours: float = 7.0,
) -> datetime:
    """Build timezone-aware local datetime and convert to UTC."""
    year_ad = year - 543 if year > 2400 else year
    local_tz = timezone(timedelta(hours=timezone_offset_hours))
    local_dt = datetime(
        year_ad, month, day, hour, minute, tzinfo=local_tz
    )
    return local_dt.astimezone(timezone.utc)


def _calculate_natal_from_utc(
    birth_dt_utc: datetime,
    latitude: float,
    longitude: float,
    location_name: str,
    *,
    displayed_year: Optional[int] = None,
    displayed_timezone: str = "Asia/Bangkok",
    birth_time_accuracy: str = "exact",
    house_system: str = "Placidus",
) -> NormalizedChart:
    """
    Canonical natal calculation.

    Swiss Ephemeris expects UTC Julian Day for calc_ut.
    House calculations are performed using the same UT day and local
    geographic coordinates.
    """
    if birth_dt_utc.tzinfo is None:
        birth_dt_utc = birth_dt_utc.replace(tzinfo=timezone.utc)
    birth_dt_utc = birth_dt_utc.astimezone(timezone.utc)

    jd = swe.julday(
        birth_dt_utc.year,
        birth_dt_utc.month,
        birth_dt_utc.day,
        birth_dt_utc.hour
        + birth_dt_utc.minute / 60.0
        + birth_dt_utc.second / 3600.0,
    )

    if house_system != "Placidus":
        raise ValueError(
            "T2 currently supports Placidus only. "
            "Add another house system explicitly in a later version."
        )

    cusps_raw, ascmc = swe.houses(
        jd,
        float(latitude),
        float(longitude),
        b"P",
    )
    cusps = tuple(float(c) for c in cusps_raw[:12])

    planets: Dict[str, ChartPoint] = {}
    for name, planet_id in PLANETS.items():
        point = _calc_point(name, planet_id, jd)
        point.house = _assign_house(point.degree_raw, cusps)
        planets[name] = point

    asc_deg = float(ascmc[0]) % 360.0
    mc_deg = float(ascmc[1]) % 360.0
    angles = _make_angles(asc_deg, mc_deg)

    houses = _build_house_cusps(cusps)

    # Birth date is represented in the user-facing timezone where known.
    # When the caller supplied a UTC-only datetime, preserve its calendar date
    # as the displayed date rather than inventing a local conversion.
    if displayed_year is None:
        local_tz = timezone(timedelta(hours=7))
        local_dt = birth_dt_utc.astimezone(local_tz)
        display_date = local_dt.date().isoformat()
        display_time = local_dt.strftime("%H:%M")
    else:
        display_date = birth_dt_utc.astimezone(
            timezone(timedelta(hours=7))
        ).date().isoformat()
        display_time = birth_dt_utc.astimezone(
            timezone(timedelta(hours=7))
        ).strftime("%H:%M")

    birth_data = BirthData(
        date=display_date,
        time=display_time,
        location_name=location_name,
        latitude=float(latitude),
        longitude=float(longitude),
        timezone=displayed_timezone,
        birth_time_accuracy=birth_time_accuracy,
    )

    settings = ChartSettings(
        zodiac="tropical",
        house_system=house_system,
        node_type="mean",
        ephemeris_version=str(getattr(swe, "version", "unknown")),
    )

    natal = NatalChart(
        schema_version="1.0",
        birth_data=birth_data,
        settings=settings,
        planets=planets,
        angles=angles,
        houses=houses,
        house_rulers={},
        aspects=[],
    )

    return NormalizedChart(
        schema_version="1.0",
        natal=natal,
        transits={},
    )


def calculate_natal_chart(
    day: int,
    month: int,
    year_buddhist: int,
    hour: int,
    minute: int,
    location_name: str = "กรุงเทพมหานคร",
) -> NormalizedChart:
    """
    Existing public signature preserved for current frontend/API migration.

    Returns:
        NormalizedChart
    """
    lat, lon = get_coordinates(location_name)
    birth_dt_utc = _resolve_birth_datetime(
        day=day,
        month=month,
        year=year_buddhist,
        hour=hour,
        minute=minute,
        timezone_offset_hours=7.0,
    )
    return _calculate_natal_from_utc(
        birth_dt_utc,
        lat,
        lon,
        location_name,
        displayed_year=year_buddhist,
        displayed_timezone="Asia/Bangkok",
        birth_time_accuracy="exact",
        house_system="Placidus",
    )


def calculate_chart(
    *args,
    **kwargs,
) -> NormalizedChart:
    """
    Migration-safe alias.

    Supported forms:

    1) Current legacy form:
       calculate_chart(day, month, year, hour, minute, location_name)

    2) Existing main.py transitional form:
       calculate_chart(birth_dt_utc, latitude, longitude)

    Form (2) intentionally returns NormalizedChart. The API layer must be
    migrated in the next phase to consume the canonical contract.
    """
    if args and isinstance(args[0], datetime):
        birth_dt_utc = args[0]
        if len(args) < 3:
            raise TypeError(
                "calculate_chart(datetime_utc, latitude, longitude) requires 3 arguments"
            )
        latitude = float(args[1])
        longitude = float(args[2])
        location_name = kwargs.get("location_name", "Unknown")
        return _calculate_natal_from_utc(
            birth_dt_utc,
            latitude,
            longitude,
            location_name,
            displayed_timezone="UTC",
            birth_time_accuracy="exact",
            house_system="Placidus",
        )

    return calculate_natal_chart(*args, **kwargs)


# Existing alias preserved for migration.

def get_realtime_transits() -> dict:
    """
    Legacy-compatible transit endpoint for the current API.

    T2 keeps the existing JSON shape so existing frontend/API code does not
    fail while the dedicated Transit Engine is migrated later.
    """
    now = datetime.now(timezone.utc)
    jul_day = swe.julday(
        now.year,
        now.month,
        now.day,
        now.hour + now.minute / 60.0 + now.second / 3600.0,
    )

    transits = {}
    for name, planet_id in PLANETS.items():
        result, _flag = swe.calc_ut(jul_day, planet_id)
        degree = float(result[0]) % 360.0
        dms = deg_to_dms(degree)
        transits[name] = {
            "deg_dec": round(degree, 6),
            "degree_raw": round(degree, 6),
            "sign": dms["sign"],
            "dms": dms["dms_str"],
            "timestamp_utc": now.isoformat(),
        }
    return transits


calculate_current_transits = get_realtime_transits

