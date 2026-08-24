from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from . import db
from .models import Exercise, Workout, WorkoutExercise
from .schemas import ExerciseSchema, WorkoutCreateSchema, WorkoutSchema, WorkoutUpdateSchema

api = Blueprint("api", __name__)
exercise_schema = ExerciseSchema()
exercise_update_schema = ExerciseSchema(partial=True)
exercises_schema = ExerciseSchema(many=True)
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_create_schema = WorkoutCreateSchema()
workout_update_schema = WorkoutUpdateSchema()


def error(message, status=400):
    return jsonify({"error": message}), status


@api.errorhandler(ValidationError)
def handle_validation(exc):
    return jsonify({"error": "Validation failed", "messages": exc.messages}), 400


@api.get("/health")
def health():
    return jsonify({"status": "ok"})


@api.route("/exercises", methods=["GET", "POST"])
def exercises():
    if request.method == "GET":
        return jsonify(exercises_schema.dump(Exercise.query.order_by(Exercise.name).all()))

    exercise = Exercise(**exercise_schema.load(request.get_json(silent=True) or {}))
    db.session.add(exercise)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("An exercise with that name already exists.", 409)
    return jsonify(exercise_schema.dump(exercise)), 201


@api.get("/exercises/<int:exercise_id>")
def get_exercise(exercise_id):
    exercise = db.get_or_404(Exercise, exercise_id)
    return jsonify(exercise_schema.dump(exercise))


@api.patch("/exercises/<int:exercise_id>")
def update_exercise(exercise_id):
    exercise = db.get_or_404(Exercise, exercise_id)
    changes = exercise_update_schema.load(request.get_json(silent=True) or {})
    if not changes:
        return error("At least one exercise field is required.")
    for field, value in changes.items():
        setattr(exercise, field, value)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("An exercise with that name already exists.", 409)
    return jsonify(exercise_schema.dump(exercise))


@api.delete("/exercises/<int:exercise_id>")
def delete_exercise(exercise_id):
    exercise = db.get_or_404(Exercise, exercise_id)
    if exercise.workout_uses:
        return error("Cannot delete an exercise used by a workout.", 409)
    db.session.delete(exercise)
    db.session.commit()
    return "", 204


@api.route("/workouts", methods=["GET", "POST"])
def workouts():
    if request.method == "GET":
        return jsonify(workouts_schema.dump(Workout.query.order_by(Workout.id).all()))

    payload = workout_create_schema.load(request.get_json(silent=True) or {})
    exercise_items = payload.pop("exercises")
    workout = Workout(**payload)
    for item in exercise_items:
        exercise = db.session.get(Exercise, item.pop("exercise_id"))
        if exercise is None:
            return error("Referenced exercise was not found.", 404)
        workout.exercises.append(WorkoutExercise(exercise=exercise, **item))
    db.session.add(workout)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("A workout cannot contain the same exercise more than once.", 409)
    return jsonify(workout_schema.dump(workout)), 201


@api.get("/workouts/<int:workout_id>")
def get_workout(workout_id):
    workout = db.get_or_404(Workout, workout_id)
    return jsonify(workout_schema.dump(workout))


@api.patch("/workouts/<int:workout_id>")
def update_workout(workout_id):
    workout = db.get_or_404(Workout, workout_id)
    changes = workout_update_schema.load(request.get_json(silent=True) or {})
    exercise_items = changes.pop("exercises", None)
    if not changes and exercise_items is None:
        return error("At least one workout field is required.")

    replacement_exercises = []
    if exercise_items is not None:
        for item in exercise_items:
            item = dict(item)
            exercise = db.session.get(Exercise, item.pop("exercise_id"))
            if exercise is None:
                return error("Referenced exercise was not found.", 404)
            replacement_exercises.append(WorkoutExercise(exercise=exercise, **item))

    for field, value in changes.items():
        setattr(workout, field, value)
    if exercise_items is not None:
        workout.exercises = replacement_exercises
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("A workout cannot contain the same exercise more than once.", 409)
    return jsonify(workout_schema.dump(workout))


@api.delete("/workouts/<int:workout_id>")
def delete_workout(workout_id):
    workout = db.get_or_404(Workout, workout_id)
    db.session.delete(workout)
    db.session.commit()
    return "", 204