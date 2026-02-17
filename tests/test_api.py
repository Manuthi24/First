from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_chat_returns_answer_for_known_question() -> None:
    response = client.post('/chat', json={'message': 'How can I track my order?', 'top_k': 3})
    assert response.status_code == 200
    payload = response.json()
    assert payload['fallback'] is False
    assert payload['sources']
    assert 'tracking' in payload['answer'].lower()


def test_chat_fallback_for_unknown_question() -> None:
    response = client.post('/chat', json={'message': 'Explain black hole singularity equations'})
    assert response.status_code == 200
    payload = response.json()
    assert payload['fallback'] is True
