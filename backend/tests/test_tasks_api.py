from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pytest
from unittest.mock import AsyncMock, patch
import asyncio

from app.database import Base, get_db
from main import app
from app.services.ssh_service import ssh_manager

# Setup Test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Helper to clear DB
def clear_db():
    db = TestingSessionLocal()
    db.execute(text("DELETE FROM health_rules"))
    db.execute(text("DELETE FROM tasks"))
    db.execute(text("DELETE FROM nodes"))
    db.commit()
    db.close()

@pytest.fixture(scope="module")
def setup():
    clear_db()
    
    # Create a node
    client.post("/api/nodes/", json={
        "name": "test-node",
        "host": "127.0.0.1",
        "port": 22,
        "username": "user",
        "password": "password"
    })
    yield
    clear_db()

def test_create_task(setup):
    # Get node id
    nodes = client.get("/api/nodes/").json()
    node_id = nodes[0]["id"]

    response = client.post("/api/tasks/", json={
        "name": "test-task",
        "node_ids": [node_id],
        "log_file_path": "/var/log/test.log",
        "start_command": "start.sh",
        "stop_command": "stop.sh",
        "health_rules": [
            {"rule_type": "keyword", "rule_content": "ERROR"}
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "test-task"
    assert len(data[0]["health_rules"]) == 1

def test_read_tasks(setup):
    response = client.get("/api/tasks/")
    assert response.status_code == 200
    assert len(response.json()) >= 1

@patch('app.routers.tasks.ssh_manager.execute_command', new_callable=AsyncMock)
def test_task_action(mock_execute, setup):
    mock_execute.return_value = "Command Executed"
    
    tasks = client.get("/api/tasks/").json()
    task_id = tasks[0]["id"]
    
    response = client.post(f"/api/tasks/{task_id}/action", json={"action": "start"})
    assert response.status_code == 200
    assert response.json()["output"] == "Command Executed"
    
    # Verify status changed (requires re-fetching or implementation detail check)
    response = client.get(f"/api/tasks/{task_id}")
    assert response.json()["status"] == "running"

@patch('app.routers.tasks.ssh_manager.stream_log') # Patching the generator
def test_websocket_log(mock_stream, setup):
    # Mocking async generator
    async def async_gen(*args, **kwargs):
        yield "Line 1"
        yield "Line 2"
    
    mock_stream.side_effect = async_gen

    tasks = client.get("/api/tasks/").json()
    task_id = tasks[0]["id"]

    with client.websocket_connect(f"/api/tasks/{task_id}/log_stream") as websocket:
        data = websocket.receive_text()
        assert data == "Line 1"
        data = websocket.receive_text()
        assert data == "Line 2"
