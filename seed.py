from app import create_app, db
from app.models import Exercise, Workout, WorkoutExercise

app = create_app()


with app.app_context():
    if Exercise.query.count() == 0:
        squat = Exercise(name="Back Squat", muscle_group="Legs", description="Barbell squat to parallel.")
        push_up = Exercise(name="Push-Up", muscle_group="Chest")
        row = Exercise(name="Dumbbell Row", muscle_group="Back")
        workout = Workout(name="Full Body Foundation", description="A balanced starter session.")
        workout.exercises = [
            WorkoutExercise(exercise=squat, sets=4, reps=8, position=1),
            WorkoutExercise(exercise=push_up, sets=3, reps=12, position=2),
            WorkoutExercise(exercise=row, sets=3, reps=10, position=3),
        ]
        db.session.add(workout)
        db.session.commit()
        print("Seed data created.")
    else:
        print("Seed data already exists.")