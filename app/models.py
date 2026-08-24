from datetime import datetime, timezone

from . import db


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
        order_by="WorkoutExercise.position",
    )


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    muscle_group = db.Column(db.String(80), nullable=True)
    workout_uses = db.relationship("WorkoutExercise", back_populates="exercise")


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"
    __table_args__ = (
        db.UniqueConstraint("workout_id", "exercise_id", name="uq_workout_exercise"),
        db.CheckConstraint("sets IS NOT NULL OR reps IS NOT NULL OR duration_seconds IS NOT NULL", name="ck_metric_present"),
        db.CheckConstraint("sets IS NULL OR sets > 0", name="ck_sets_positive"),
        db.CheckConstraint("reps IS NULL OR reps > 0", name="ck_reps_positive"),
        db.CheckConstraint("duration_seconds IS NULL OR duration_seconds > 0", name="ck_duration_positive"),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id", ondelete="RESTRICT"), nullable=False)
    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.Integer, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
    position = db.Column(db.Integer, nullable=False, default=1)
    workout = db.relationship("Workout", back_populates="exercises")
    exercise = db.relationship("Exercise", back_populates="workout_uses")