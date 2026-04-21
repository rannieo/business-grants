import json
import pytest
from pathlib import Path
from pipeline.retriever import Retriever


@pytest.fixture
def grants():
    path = Path(__file__).parent.parent.parent / "grants.json"
    return json.loads(path.read_text())


@pytest.fixture
def retriever(grants):
    return Retriever(grants)


def test_retrieves_mra_for_overseas_expansion(retriever):
    msg = "We want to expand overseas into Malaysia for the first time."
    results = retriever.retrieve(msg, [], k=5)
    ids = [g["id"] for g in results]
    assert "mra" in ids


def test_retrieves_edg_npd_for_new_product(retriever):
    msg = "We are building a new AI product from scratch and need R&D funding."
    results = retriever.retrieve(msg, [], k=5)
    ids = [g["id"] for g in results]
    assert "edg_npd" in ids


def test_retrieves_edg_automation_for_automation(retriever):
    msg = "We want to automate our manual invoice processing to improve productivity."
    results = retriever.retrieve(msg, [], k=5)
    ids = [g["id"] for g in results]
    assert "edg_automation" in ids


def test_retrieves_ccp_for_hiring_and_reskilling(retriever):
    msg = "We are hiring new staff and want to reskill them into redesigned roles."
    results = retriever.retrieve(msg, [], k=5)
    ids = [g["id"] for g in results]
    assert "ccp" in ids


def test_respects_k_limit(retriever):
    msg = "We want to expand overseas, automate, hire, and build a new product."
    results = retriever.retrieve(msg, [], k=3)
    assert len(results) <= 3


def test_accumulates_history_for_scoring(retriever):
    history = [
        {"role": "user", "content": "We are a Singapore tech company."},
    ]
    msg = "We want to expand overseas to Malaysia."
    results = retriever.retrieve(msg, history, k=5)
    ids = [g["id"] for g in results]
    assert "mra" in ids


def test_returns_list_of_dicts(retriever):
    results = retriever.retrieve("We want to innovate and build new products.", [], k=5)
    assert isinstance(results, list)
    for g in results:
        assert isinstance(g, dict)
        assert "id" in g
