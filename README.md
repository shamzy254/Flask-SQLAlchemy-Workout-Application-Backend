# Workout Tracking API

A Flask, SQLAlchemy, and Marshmallow backend for personal trainers to manage reusable exercises and workouts. Trainers can define an exercise once, reuse it across workouts, and attach set, rep, or duration prescriptions to each workout entry.

The API supports exercise and workout CRUD operations, nested workout serialization, validation, database constraints, and SQLite by default.

## Installation

Python 3.8 or newer and Pipenv are recommended.

```bash
git clone https://github.com/shamzy254/Flask-SQLAlchemy-Workout-Application-Backend.git
cd Flask-SQLAlchemy-Workout-Application-Backend
pipenv install --dev
pipenv shell
```

The `Pipfile` defines Python 3.8 and these dependencies:

| Dependency | Version |
| --- | --- |
| Flask | 3.0.3 |
| Flask-SQLAlchemy | 3.1.1 |
| Flask-Marshmallow | 1.2.1 |
| Marshmallow | 3.22.0 |
| Marshmallow-SQLAlchemy | 1.1.1 |
| Pytest | 8.3.5 (development) |

The application currently creates its configured database tables automatically when it starts with `db.create_all()`. Flask-Migrate is not configured in the application, so there is no `flask db upgrade` step at this time. Seed the example exercises and workout with:

```bash
pipenv run python seed.py
```

By default, SQLite stores the database in `instance/workouts.db` (or the path configured by `DATABASE_URL`). Run `seed.py` again safely; it does not duplicate the example data.

## Run

```bash
pipenv run flask --app run run --debug
```

The API is available under `/api`. To use another database, set `DATABASE_URL` before starting the application.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/health` | Returns an API health status. |
| GET | `/api/exercises` | Lists reusable exercises, ordered by name. |
| POST | `/api/exercises` | Creates an exercise. Names must be unique and 1-120 characters. |
| GET | `/api/exercises/<id>` | Returns one exercise or `404`. |
| PATCH | `/api/exercises/<id>` | Updates one or more exercise fields. |
| DELETE | `/api/exercises/<id>` | Deletes an unused exercise; returns `409` when it is referenced by a workout. |
| GET | `/api/workouts` | Lists workouts and their prescribed exercises. |
| POST | `/api/workouts` | Creates a workout, optionally with exercise prescriptions. |
| GET | `/api/workouts/<id>` | Returns one workout with its exercises or `404`. |
| PATCH | `/api/workouts/<id>` | Updates workout fields; supplying `exercises` replaces its prescriptions. |
| DELETE | `/api/workouts/<id>` | Deletes a workout and its associated prescriptions. |

When creating a workout, `exercises` is an array of objects. Each object requires an existing `exercise_id` and at least one positive value among `sets`, `reps`, and `duration_seconds`. An exercise can be reused across workouts but only once within the same workout.

Example request:

```json
{
	"name": "Lower Body Strength",
	"description": "Tuesday session",
	"exercises": [
		{"exercise_id": 1, "sets": 4, "reps": 8, "position": 1},
		{"exercise_id": 2, "duration_seconds": 45, "position": 2}
	]
}
```

## Tests

Run the test suite with:

```bash
pipenv run python -m pytest -q
```

The test file is [`tests/test_api.py`](tests/test_api.py). It covers exercise reuse, validation, uniqueness, missing references, workout deletion, updates, model validation, and relationship serialization. Tests use an in-memory SQLite database so they do not modify the development database.