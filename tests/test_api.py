def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "message" in resp.json()

def test_create_paper(client, test_paper_id, test_user_id):
    paper = {
        "paper_id": test_paper_id,
        "title": "Test 4D Paper",
        "research_purpose": "Test research",
        "creator": test_user_id
    }
    resp = client.post("/api/papers/create", json=paper)
    assert resp.status_code in (200, 400)  # 400 means already exists