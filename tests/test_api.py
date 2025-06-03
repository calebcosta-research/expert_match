import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
if os.path.exists('test.db'):
    os.remove('test.db')
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_create_expert():
    resp = client.post('/experts/', json={'name': 'Alice', 'email': 'alice@example.com'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['name'] == 'Alice'
    assert data['email'] == 'alice@example.com'
