import pytest
from chart_schema import (
    BirthData, ChartPoint, ChartSettings, HouseCusp, NatalChart
)
from house_ruler_engine import calculate_house_rulers, TRADITIONAL_RULERS


def mk_point(name, degree, sign, house):
    return ChartPoint(
        name=name,
        degree_raw=degree,
        sign=sign,
        degree_in_sign=int(degree % 30),
        minute=0,
        second=0,
        dms=f'{int(degree % 30)}°{sign} 0\'0"',
        house=house,
        retrograde=False,
        point_type="planet",
    )


def mk_cusp(house, degree, sign):
    return HouseCusp(
        house=house,
        degree_raw=degree,
        sign=sign,
        degree_in_sign=int(degree % 30),
        minute=0,
        second=0,
        dms=f'{int(degree % 30)}°{sign} 0\'0"',
    )


def make_chart():
    birth = BirthData(
        date="1965-05-27",
        time="10:30",
        location_name="กรุงเทพมหานคร",
        latitude=13.7563,
        longitude=100.5018,
    )
    settings = ChartSettings()
    planets = {
        "Sun": mk_point("Sun", 33, "Taurus", 9),
        "Moon": mk_point("Moon", 132, "Leo", 1),
        "Mercury": mk_point("Mercury", 39, "Taurus", 9),
        "Venus": mk_point("Venus", 20, "Aries", 9),
        "Mars": mk_point("Mars", 21, "Aries", 9),
        "Jupiter": mk_point("Jupiter", 71, "Gemini", 10),
        "Saturn": mk_point("Saturn", 131, "Leo", 12),
        "Uranus": mk_point("Uranus", 218, "Scorpio", 3),
        "Neptune": mk_point("Neptune", 255, "Sagittarius", 5),
        "Pluto": mk_point("Pluto", 191, "Libra", 3),
        "Chiron": mk_point("Chiron", 33, "Taurus", 9),
        "NorthNode": mk_point("NorthNode", 202, "Libra", 3),
    }
    signs = [
        "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
        "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
    ]
    houses={}
    for i, sign in enumerate(signs,1):
        houses[f"House_{i}"]=mk_cusp(i,(i-1)*30,sign)
    return NatalChart(
        birth_data=birth,
        settings=settings,
        planets=planets,
        angles={},
        houses=houses,
    )


def test_traditional_rulers_complete():
    assert len(TRADITIONAL_RULERS) == 12
    assert TRADITIONAL_RULERS["Aries"] == "Mars"
    assert TRADITIONAL_RULERS["Scorpio"] == "Mars"
    assert TRADITIONAL_RULERS["Aquarius"] == "Saturn"
    assert TRADITIONAL_RULERS["Pisces"] == "Jupiter"


def test_all_12_house_rulers_created():
    chart = make_chart()
    result = calculate_house_rulers(chart)
    assert len(result) == 12
    for i in range(1,13):
        assert f"House_{i}" in result


def test_house_1_aries_ruler_is_mars():
    chart = make_chart()
    result = calculate_house_rulers(chart)
    r=result["House_1"]
    assert r.cusp_sign == "Aries"
    assert r.ruler_planet == "Mars"
    assert r.ruler_house == 9


def test_house_10_capricorn_ruler_is_saturn():
    chart = make_chart()
    result = calculate_house_rulers(chart)
    r=result["House_10"]
    assert r.cusp_sign == "Capricorn"
    assert r.ruler_planet == "Saturn"
    assert r.ruler_house == 12


def test_missing_cusp_raises():
    chart = make_chart()
    del chart.houses["House_12"]
    with pytest.raises(ValueError):
        calculate_house_rulers(chart)


def test_missing_ruler_planet_raises():
    chart = make_chart()
    del chart.planets["Mars"]
    with pytest.raises(ValueError):
        calculate_house_rulers(chart)
