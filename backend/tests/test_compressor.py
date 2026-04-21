import json
import pytest
from pathlib import Path
from pipeline.compressor import Compressor


@pytest.fixture
def grants():
    path = Path(__file__).parent.parent.parent / "grants.json"
    return json.loads(path.read_text())


@pytest.fixture
def compressor():
    return Compressor()


def test_strips_supports_field(compressor, grants):
    result = compressor.compress(grants[:3])
    for g in result:
        assert "supports" not in g


def test_keeps_id_and_name(compressor, grants):
    result = compressor.compress(grants[:3])
    for g in result:
        assert "id" in g
        assert "name" in g


def test_keeps_business_goals(compressor, grants):
    result = compressor.compress(grants[:3])
    for g in result:
        assert "business_goals" in g


def test_keeps_notes(compressor, grants):
    result = compressor.compress(grants[:3])
    for g in result:
        assert "notes" in g


def test_keeps_eligibility_fields(compressor, grants):
    result = compressor.compress(grants[:3])
    for g in result:
        assert "applicant_type" in g
        assert "employee_count_min" in g
        assert "requires_new_market" in g


def test_preserves_grant_count(compressor, grants):
    subset = grants[:4]
    result = compressor.compress(subset)
    assert len(result) == 4


def test_empty_input_returns_empty(compressor):
    assert compressor.compress([]) == []
