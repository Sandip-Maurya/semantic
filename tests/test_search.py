# tests/test_search.py
import pytest

# (query, expected_top_name)
SEARCH_CASES = [
    ("latest Apple smartphone", "Apple iPhone 15 Pro"),
    ("electric car with autopilot", "Tesla Model 3"),
    ("lightweight laptop for students", "MacBook Air M3"),
    ("best noise cancelling headphones", "Sony WH-1000XM5"),
    ("how to build a startup", "The Lean Startup"),
    ("comfortable running shoes for training", "Nike Air Zoom Pegasus 41"),
    ("Android device with stylus for drawing", "Samsung Galaxy Tab S9"),
    ("portable Bluetooth audio device", "Bose SoundLink Revolve+"),
    ("tool to organize tasks and notes", "Notion"),
    ("device for reading ebooks", "Kindle Paperwhite"),
]


@pytest.mark.parametrize("query,expected_name", SEARCH_CASES)
def test_semantic_search_top1(test_client, query, expected_name):
    resp = test_client.post("/search", json={"query": query})
    print(resp.content)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0

    top = data[0]
    # some apps return name directly, some return in "item" — adjust if needed
    assert top["name"] == expected_name
