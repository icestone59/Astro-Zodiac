import math

from chart_schema import Aspect, BirthData, ChartPoint, ChartSettings, HouseCusp, HouseRuler, NatalChart, NormalizedChart
from pattern_engine import calculate_patterns


def point(name, degree, sign, house=None, point_type="planet"):
    return ChartPoint(
        name=name, degree_raw=degree, sign=sign, degree_in_sign=int(degree % 30),
        minute=0, second=0, dms=f"{degree:.2f}°", house=house,
        retrograde=False, point_type=point_type,
    )


def base_chart():
    planets = {
        "Sun": point("Sun", 10, "Aries", 10),
        "Moon": point("Moon", 130, "Leo", 1),
        "Mercury": point("Mercury", 12, "Aries", 9),
        "Venus": point("Venus", 200, "Libra", 7),
        "Mars": point("Mars", 102, "Cancer", 6),
        "Jupiter": point("Jupiter", 190, "Libra", 7),
        "Saturn": point("Saturn", 192, "Libra", 10),
        "Uranus": point("Uranus", 310, "Aquarius", 12),
        "Neptune": point("Neptune", 12, "Aries", 12),
        "Pluto": point("Pluto", 150, "Virgo", 3),
        "Chiron": point("Chiron", 30, "Taurus", 2, "chiron"),
        "NorthNode": point("NorthNode", 45, "Taurus", 3, "node"),
    }
    houses = {}
    for n in range(1, 13):
        houses[f"House_{n}"] = HouseCusp(
            house=n, degree_raw=float((n - 1) * 30), sign=["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"][n-1],
            degree_in_sign=0, minute=0, second=0, dms="0°",
        )
    rulers = {}
    for n in range(1, 13):
        rulers[f"House_{n}"] = HouseRuler(
            house=n, cusp_sign=houses[f"House_{n}"].sign,
            ruler_planet={"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}[houses[f"House_{n}"].sign],
            ruler_degree_raw=planets[{"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}[houses[f"House_{n}"].sign]].degree_raw,
            ruler_sign="Libra", ruler_house=10, ruler_dms="0°",
        )
    aspects = [
        Aspect(p1="Mars", p2="Saturn", aspect="square", symbol="□", exact_angle=90, orb=0.2),
        Aspect(p1="Mercury", p2="Saturn", aspect="conjunction", symbol="☌", exact_angle=0, orb=0.4),
        Aspect(p1="Sun", p2="Jupiter", aspect="opposition", symbol="☍", exact_angle=180, orb=1.0),
    ]
    birth = BirthData(date="2000-01-01", time="12:00", location_name="Test", latitude=13.7, longitude=100.5)
    natal = NatalChart(birth_data=birth, settings=ChartSettings(), planets=planets, angles={}, houses=houses, house_rulers=rulers, aspects=aspects)
    return NormalizedChart(natal=natal)


def test_returns_mvp_patterns_and_top3():
    result = calculate_patterns(base_chart())
    ids = [c.pattern_id for c in result.ranking.candidates]
    assert ids == sorted(ids, key=lambda x: (-next(c for c in result.ranking.candidates if c.pattern_id == x).score.total, x))
    assert len(result.ranking.candidates) == 6
    assert result.ranking.primary is not None
    assert result.ranking.secondary is not None
    assert result.ranking.strength is not None
    assert result.ranking.strength.pattern_id == "S01"


def test_pattern_is_exploratory_not_diagnosis():
    result = calculate_patterns(base_chart())
    assert all(c.status == "candidate" for c in result.ranking.candidates)
    assert all(c.language == "pattern_to_explore" for c in result.ranking.candidates)
