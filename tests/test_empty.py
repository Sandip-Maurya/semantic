

def test_search_empty_query_returns_400(test_client):
    resp = test_client.post("/search")
    print(resp)
    assert resp.status_code in (400, 422)
