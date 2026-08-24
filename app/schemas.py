from marshmallow import EXCLUDE, Schema, ValidationError, fields, validate, validates_schema


positive = validate.Range(min=1)
non_blank_name = validate.And(validate.Length(min=1, max=120), validate.Regexp(r".*\S.*"))
name = fields.Str(required=True, validate=non_blank_name, allow_none=False)


class ExerciseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    name = name
    description = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    muscle_group = fields.Str(allow_none=True, validate=validate.Length(max=80))


class WorkoutExerciseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    exercise_id = fields.Int(required=True, validate=positive)
    exercise = fields.Nested(ExerciseSchema, dump_only=True)
    sets = fields.Int(allow_none=True, validate=positive)
    reps = fields.Int(allow_none=True, validate=positive)
    duration_seconds = fields.Int(allow_none=True, validate=positive)
    position = fields.Int(load_default=1, validate=positive)

    @validates_schema
    def require_metric(self, data, **kwargs):
        if not any(data.get(metric) is not None for metric in ("sets", "reps", "duration_seconds")):
            raise ValidationError("At least one of sets, reps, or duration_seconds is required.")


class WorkoutSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    name = name
    description = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    created_at = fields.DateTime(dump_only=True)
    exercises = fields.Nested(WorkoutExerciseSchema, many=True, dump_only=True)


class WorkoutCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = name
    description = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    exercises = fields.List(fields.Nested(WorkoutExerciseSchema), load_default=list, validate=validate.Length(max=100))


class WorkoutUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(validate=non_blank_name, allow_none=False)
    description = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    exercises = fields.List(fields.Nested(WorkoutExerciseSchema), validate=validate.Length(max=100))
