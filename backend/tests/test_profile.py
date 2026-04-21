import pytest

from pipeline.profile import ConversationProfileExtractor


@pytest.fixture
def extractor():
    return ConversationProfileExtractor()


def test_extracts_employee_count_from_explicit_phrase(extractor):
    profile = extractor.extract("We are a Singapore company with 12 employees.", [])
    assert profile.employee_count == 12


def test_extracts_employee_count_from_range_option(extractor):
    profile = extractor.extract("11-30 employees", [])
    assert profile.employee_count == 11


def test_extracts_local_entity_true(extractor):
    profile = extractor.extract("Yes, we are registered in Singapore.", [])
    assert profile.local_entity is True


def test_extracts_local_entity_false_from_negation(extractor):
    profile = extractor.extract("No, we are not based in Singapore.", [])
    assert profile.local_entity is False


def test_extracts_new_market_true(extractor):
    profile = extractor.extract("This is our first time entering that market.", [])
    assert profile.new_market is True


def test_extracts_new_market_false(extractor):
    profile = extractor.extract("This is not a new market for us.", [])
    assert profile.new_market is False


def test_extracts_applicant_type_non_sme(extractor):
    profile = extractor.extract("We are a non-SME large enterprise.", [])
    assert profile.applicant_type == "non_sme"


def test_extracts_revenue_band_under_100m(extractor):
    profile = extractor.extract("Our annual revenue is under 100M.", [])
    assert profile.revenue_band == "under_100m"


def test_extracts_revenue_band_over_100m(extractor):
    profile = extractor.extract("Our annual revenue is above 100M.", [])
    assert profile.revenue_band == "over_100m"


def test_later_message_overrides_earlier_signal(extractor):
    history = [{"role": "user", "content": "We are based in Singapore."}]
    profile = extractor.extract("Actually we are not based in Singapore.", history)
    assert profile.local_entity is False
