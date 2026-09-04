import pytest
from chart_schema import ChartPoint
from aspect_engine import (
    calculate_major_aspects,
    circular_distance,
    find_aspect,
)


def point(name, degree, sign="Aries"):
    return ChartPoint(
        name=name,
        degree_raw=degree,
        sign=sign,
        degree_in_sign=int(degree % 30),
        minute=0,
        second=0,
        dms=f'{int(degree % 30)}°{sign} 0\'0"',
        house=1,
        retrograde=False,
        point_type="planet",
    )


def test_circular_distance_wraparound():
    assert circular_distance(359, 1) == pytest.approx(2)
    assert circular_distance(10, 350) == pytest.approx(20)


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (10, 10, "conjunction"),
        (10, 70, "sextile"),
        (10, 100, "square"),
        (10, 130, "trine"),
        (10, 190, "opposition"),
    ],
)
def test_major_aspects(a,b,expected):
    result=find_aspect(point("Sun",a), point("Mars",b))
    assert result is not None
    assert result.aspect == expected


def test_outside_orb_returns_none():
    # Sun default 8°; exact square is 90°, difference is 10°.
    result=find_aspect(point("Sun",0), point("Mars",100))
    assert result is None


def test_nearest_aspect_wins():
    # 178° is nearer opposition than trine.
    result=find_aspect(point("Sun",0), point("Mars",178))
    assert result is not None
    assert result.aspect == "opposition"
    assert result.orb == pytest.approx(2)


def test_unique_pairs():
    points=[
        point("Sun",0),
        point("Moon",90),
        point("Mercury",180),
    ]
    aspects=calculate_major_aspects(points)
    assert len(aspects) == 3


def test_sorted_deterministically():
    points=[
        point("Mercury",0),
        point("Sun",180),
        point("Moon",90),
    ]
    a=calculate_major_aspects(points)
    b=calculate_major_aspects(points)
    assert [x.model_dump() for x in a] == [x.model_dump() for x in b]


def test_applying_left_none_in_t4():
    result=find_aspect(point("Sun",0), point("Mars",60))
    assert result.applying is None
