import pytest

from app import create_app, db
from app.models import Exercise


@pytest.fixture()
def client():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.test_client() as client, app.app_context():
        db.drop_all()
        db.create_all()
        yield client
        db.session.remove()
        db.drop_all()


def create_exercise(client, name="Deadlift"):
    response = client.post("/api/exercises", json={"name": name, "muscle_group": "Back"})
    assert response.status_code == 201
    return response.get_json()["id"]


def test_exercise_is_reusable_in_workouts(client):
    exercise_id = create_exercise(client)
    workout = {"name": "Strength A", "exercises": [{"exercise_id": exercise_id, "sets": 3, "reps": 5}]}
    first = client.post("/api/workouts", json=workout)
    second = client.post("/api/workouts", json={**workout, "name": "Strength B"})
    assert first.status_code == second.status_code == 201
    assert first.get_json()["exercises"][0]["exercise"]["name"] == "Deadlift"


def test_validation_and_unique_constraint(client):
    assert client.post("/api/exercises", json={"name": ""}).status_code == 400
    create_exercise(client)
    assert client.post("/api/exercises", json={"name": "Deadlift"}).status_code == 409

    exercise_id = Exercise.query.first().id
    invalid = client.post("/api/workouts", json={"name": "Invalid", "exercises": [{"exercise_id": exercise_id}]})
    assert invalid.status_code == 400


def test_missing_exercise_and_delete_workout(client):
    missing = client.post("/api/workouts", json={"name": "Missing", "exercises": [{"exercise_id": 99, "duration_seconds": 30}]})
    assert missing.status_code == 404
    exercise_id = create_exercise(client, "Plank")
    workout = client.post("/api/workouts", json={"name": "Core", "exercises": [{"exercise_id": exercise_id, "duration_seconds": 30}]})
    assert client.delete(f"/api/workouts/{workout.get_json()['id']}").status_code == 204
    assert client.get(f"/api/workouts/{workout.get_json()['id']}").status_code == 404