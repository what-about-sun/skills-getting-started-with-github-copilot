from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
original_activities = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(deepcopy(original_activities))
    yield


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Basketball" in data


def test_signup_for_activity_success():
    email = "testuser1@mergington.edu"
    response = client.post("/activities/Basketball/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Basketball"}
    assert email in app_module.activities["Basketball"]["participants"]


def test_signup_for_unknown_activity_returns_404():
    response = client.post("/activities/UnknownActivity/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_duplicate_signup_returns_400():
    email = "duplicate@mergington.edu"
    client.post("/activities/Basketball/signup", params={"email": email})

    response = client.post("/activities/Basketball/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_success():
    response = client.delete("/activities/Chess Club/participants", params={"email": "michael@mergington.edu"})

    assert response.status_code == 200
    assert response.json() == {"message": "Removed michael@mergington.edu from Chess Club"}
    assert "michael@mergington.edu" not in app_module.activities["Chess Club"]["participants"]


def test_remove_missing_participant_returns_404():
    response = client.delete("/activities/Chess Club/participants", params={"email": "missing@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"
