from uuid import uuid4
from application_schema import BirthChartRequest
import application_service as app
from membership_schema import MembershipState
from chart_schema import BirthData, ChartPoint, ChartSettings, NatalChart, NormalizedChart, HouseCusp


def test_pipeline_version():
    assert app.pipeline_version() == "t16.1"


def _fake_chart():
    def point(name, degree, house):
        return ChartPoint(
            name=name, degree_raw=degree, sign="Aries", degree_in_sign=int(degree % 30),
            minute=0, second=0, dms=f"{int(degree % 30)}° Aries 0\'0\"",
            house=house, retrograde=False, point_type="planet" if name != "NorthNode" else "node"
        )
    birth = BirthData(
        date="1987-01-01", time="12:00", location_name="กรุงเทพมหานคร",
        latitude=13.7563, longitude=100.5018
    )
    natal = NatalChart(
        birth_data=birth, settings=ChartSettings(),
        planets={
            "Sun": point("Sun", 10, 10),
            "Moon": point("Moon", 140, 3),
            "Mercury": point("Mercury", 20, 9),
            "Venus": point("Venus", 50, 7),
            "Mars": point("Mars", 80, 6),
            "Jupiter": point("Jupiter", 95, 10),
            "Saturn": point("Saturn", 170, 12),
            "Uranus": point("Uranus", 210, 3),
            "Neptune": point("Neptune", 250, 5),
            "Pluto": point("Pluto", 300, 3),
            "NorthNode": point("NorthNode", 320, 3),
        },
        angles={
            "ASC": ChartPoint(name="ASC", degree_raw=0, sign="Aries", degree_in_sign=0, minute=0, second=0, dms="0° Aries 0\'0\"", point_type="angle"),
            "MC": ChartPoint(name="MC", degree_raw=270, sign="Capricorn", degree_in_sign=0, minute=0, second=0, dms="0° Capricorn 0\'0\"", point_type="angle"),
        },
        houses={f"House_{i}": HouseCusp(house=i, degree_raw=float((i-1)*30), sign=["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"][i-1], degree_in_sign=0, minute=0, second=0, dms="0°",) for i in range(1,13)},
        house_rulers={},
        aspects=[],
    )
    return NormalizedChart(natal=natal, transits={})

def test_free_application_pipeline(monkeypatch):
    monkeypatch.setattr(app, "calculate_natal_chart", lambda *args, **kwargs: _fake_chart())
    req = BirthChartRequest(day=1, month=1, year_buddhist=2530, hour=12, minute=0, location_name="กรุงเทพมหานคร")
    result = app.analyze_free(req)
    assert result.chart.schema_version == "1.0"
    assert result.pattern_result.ranking is not None
    assert result.evidence_snapshot.patterns is not None


def test_access_boundary():
    membership = MembershipState(user_id=uuid4(), active_products=["free"])
    decision = app.check_feature_access(membership, "action_plan")
    assert decision.allowed is False


def test_psychology_guard():
    try:
        app.build_psychology_for_validated_pattern("P01", "explored")
    except ValueError as exc:
        assert "validated pattern" in str(exc)
    else:
        raise AssertionError("unvalidated pattern must be rejected")


def test_action_plan_guard():
    try:
        app.build_action_plan_for_validated_pattern("P01", "not_confirmed", "เริ่มงานให้ไวขึ้น")
    except ValueError as exc:
        assert "validated pattern" in str(exc)
    else:
        raise AssertionError("non-validated pattern must be rejected")
