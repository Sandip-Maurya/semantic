# tests/test_search_soft.py
import pytest

SEARCH_CASES_SOFT = [
    ("latest Apple smartphone", "Apple iPhone 15 Pro"),
    ("how to build a startup", "The Lean Startup"),
    ("tool to organize tasks and notes", "Notion"),
]


@pytest.mark.parametrize("query,expected_name", SEARCH_CASES_SOFT)
def test_semantic_search_in_top3(test_client, query, expected_name):
    resp = test_client.post("/search", json={"query": query})
    assert resp.status_code == 200
    data = resp.json()
    names = [item["name"] for item in data]
    assert expected_name in names

