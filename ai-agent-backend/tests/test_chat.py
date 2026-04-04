from unittest.mock import patch


@patch("app.main.run_agent")
def test_chat_success(mock_run, client):
    mock_run.return_value = {
        "output": "Here are the users.",
        "tool_used": "get_users",
        "tool_result": [{"id": 1, "name": "Alice"}],
    }

    r = client.post(
        "/chat",
        json={"user_id": "u1", "message": "List users"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["result"] == "Here are the users."
    assert body["tool_used"] == "get_users"
    assert body["tool_result"] == [{"id": 1, "name": "Alice"}]

    mock_run.assert_called_once()
    call_kw = mock_run.call_args
    assert call_kw[0][0] == "List users"
    assert "chat_context" in call_kw[1]
    assert "memory_context" in call_kw[1]


def test_chat_validation_empty_user(client):
    r = client.post("/chat", json={"user_id": "   ", "message": "hi"})
    assert r.status_code == 422


@patch("app.main.run_agent")
def test_chat_quota_error_returns_clean_429(mock_run, client):
    mock_run.side_effect = Exception(
        "Error code: 429 - {'error': {'message': 'You exceeded your current quota', "
        "'type': 'insufficient_quota'}}"
    )

    r = client.post("/chat", json={"user_id": "u1", "message": "hi"})
    assert r.status_code == 429
    assert r.json()["detail"] == (
        "Model provider quota is exhausted. Please check your API plan/billing, then try again."
    )
