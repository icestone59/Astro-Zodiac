import pytest
from datetime import datetime, timezone

from astro_calc import (
    calculate_natal_chart,
    calculate_chart,
    deg_to_dms,
    get_coordinates,
)


def test_deg_to_dms_wraps_longitude():
    d = deg_to_dms(393.8222)
    assert d["degree_total"] == pytest.approx(33.8222, abs=1e-4)
    assert d["sign"] == "Taurus"
    assert d["degree_in_sign"] == 3


def test_known_location():
    lat, lon = get_coordinates("กรุงเทพมหานคร")
    assert lat == pytest.approx(13.7563)
    assert lon == pytest.approx(100.5018)


def test_calculate_natal_returns_normalized_chart():
    chart = calculate_natal_chart(
        27, 5, 2508, 10, 30, "กรุงเทพมหานคร"
    )
    assert chart.schema_version == "1.0"
    assert "Sun" in chart.natal.planets
    assert "Moon" in chart.natal.planets
    assert chart.natal.planets["Sun"].house is not None
    assert 1 <= chart.natal.planets["Sun"].house <= 12
    assert len(chart.natal.houses) == 12
    assert "ASC" in chart.natal.angles
    assert "MC" in chart.natal.angles


def test_all_planets_have_canonical_degree_and_house():
    chart = calculate_natal_chart(
        27, 5, 2508, 10, 30, "กรุงเทพมหานคร"
    )
    for name, point in chart.natal.planets.items():
        assert 0 <= point.degree_raw < 360
        assert point.house is not None
        assert 1 <= point.house <= 12
        assert point.sign in {
            "Aries", "Taurus", "Gemini", "Cancer",
            "Leo", "Virgo", "Libra", "Scorpio",
            "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        }


def test_transitional_datetime_signature_returns_normalized_chart():
    utc_dt = datetime(1965, 5, 27, 3, 30, tzinfo=timezone.utc)
    chart = calculate_chart(utc_dt, 13.7563, 100.5018)
    assert chart.natal.angles["ASC"].point_type == "angle"
    assert "Sun" in chart.natal.planets


def test_chart_values_are_deterministic():
    a = calculate_natal_chart(27, 5, 2508, 10, 30, "กรุงเทพมหานคร")
    b = calculate_natal_chart(27, 5, 2508, 10, 30, "กรุงเทพมหานคร")
    assert a.model_dump() == b.model_dump()
