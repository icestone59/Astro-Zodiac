import pytest
from chart_schema import ChartPoint
from uranian_engine import (
    normalize_90,
    midpoint_longitude,
    midpoint_axis,
    axis_distance,
    detect_midpoint_picture,
    calculate_90_degree_positions,
    calculate_midpoints,
    calculate_planetary_pictures,
)


def point(name, degree):
    return ChartPoint(
        name=name,
        degree_raw=degree,
        sign="Aries",
        degree_in_sign=int(degree % 30),
        minute=0,
        second=0,
        dms="0°Aries 0'0\"",
        house=1,
        retrograde=False,
        point_type="planet",
    )


def test_normalize_90():
    assert normalize_90(10) == pytest.approx(10)
    assert normalize_90(100) == pytest.approx(10)
    assert normalize_90(190) == pytest.approx(10)
    assert normalize_90(280) == pytest.approx(10)
    assert normalize_90(370) == pytest.approx(10)


def test_midpoint_longitude_simple():
    assert midpoint_longitude(10, 30) == pytest.approx(20)


def test_midpoint_longitude_wraparound():
    # shortest arc from 350° to 10° crosses 0°; midpoint = 0°
    assert midpoint_longitude(350, 10) == pytest.approx(0)


def test_midpoint_axis_folds_to_90():
    assert midpoint_axis(10, 190) == pytest.approx(10)


def test_axis_distance_wraparound():
    assert axis_distance(89, 1) == pytest.approx(2)


def test_detect_midpoint_picture_exact():
    a=point("Sun",0)
    b=point("Moon",60)
    c=point("Mars",30)
    r=detect_midpoint_picture(a,b,c,orb=0.1)
    assert r is not None
    assert r["picture"] == "Sun/Moon=Mars"
    assert r["orb"] == pytest.approx(0)


def test_detect_midpoint_picture_outside_orb():
    a=point("Sun",0)
    b=point("Moon",60)
    c=point("Mars",32)
    assert detect_midpoint_picture(a,b,c,orb=1.0) is None


def test_90_positions():
    positions=calculate_90_degree_positions([
        point("Sun",190),
        point("Moon",275),
    ])
    assert positions["Sun"] == pytest.approx(10)
    assert positions["Moon"] == pytest.approx(5)


def test_midpoint_list_deterministic():
    pts=[point("Sun",0),point("Moon",60),point("Mars",30)]
    a=calculate_midpoints(pts)
    b=calculate_midpoints(pts)
    assert a == b
    assert len(a) == 3


def test_planetary_picture_finds_expected():
    pts=[point("Sun",0),point("Moon",60),point("Mars",30),point("Venus",180)]
    pictures=calculate_planetary_pictures(pts,orb=0.1)
    labels={p["picture"] for p in pictures}
    assert "Sun/Moon=Mars" in labels
