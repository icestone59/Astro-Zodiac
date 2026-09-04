import pytest
from chart_schema import (
    BirthData, ChartPoint, ChartSettings, HouseCusp, HouseRuler,
    NatalChart, NormalizedChart
)


def point(name="Sun", degree=33.8222, sign="Taurus", house=9):
    return ChartPoint(
        name=name,
        degree_raw=degree,
        sign=sign,
        degree_in_sign=3,
        minute=49,
        second=0,
        dms="3°Taurus 49'0\"",
        house=house,
        point_type="planet",
    )


def test_chart_point_requires_canonical_degree_raw():
    p = point()
    assert p.degree_raw == 33.8222
    assert p.house == 9


def test_chart_point_rejects_unknown_fields():
    with pytest.raises(Exception):
        ChartPoint(
            name="Sun",
            degree_raw=10,
            sign="Aries",
            degree_in_sign=10,
            minute=0,
            second=0,
            dms='10°Aries 0\'0"',
            bogus="not allowed",
        )


def test_chart_point_validates_degree_range():
    with pytest.raises(Exception):
        point(degree=360)


def test_birth_data_defaults_to_bangkok_timezone():
    b = BirthData(
        date="1965-05-27",
        time="10:30",
        location_name="กรุงเทพมหานคร",
        latitude=13.7563,
        longitude=100.5018,
    )
    assert b.timezone == "Asia/Bangkok"
    assert b.birth_time_accuracy == "exact"


def test_normalized_chart_contract():
    birth = BirthData(
        date="1965-05-27",
        time="10:30",
        location_name="กรุงเทพมหานคร",
        latitude=13.7563,
        longitude=100.5018,
    )
    settings = ChartSettings()
    chart = NatalChart(
        birth_data=birth,
        settings=settings,
        planets={"Sun": point()},
        angles={},
        houses={},
    )
    normalized = NormalizedChart(natal=chart)
    payload = normalized.model_dump()
    assert payload["schema_version"] == "1.0"
    assert payload["natal"]["planets"]["Sun"]["degree_raw"] == 33.8222


def test_house_ruler_fields():
    r = HouseRuler(
        house=10,
        cusp_sign="Gemini",
        ruler_planet="Mercury",
        ruler_degree_raw=39.3667,
        ruler_sign="Taurus",
        ruler_house=9,
        ruler_dms="9°Taurus 22'0\"",
    )
    assert r.ruler_house == 9
