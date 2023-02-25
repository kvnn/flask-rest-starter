from marshmallow import Schema, fields, validate


class CreateSignupInputSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    password2 = fields.Str(required=True, validate=validate.Length(min=6))


class CreateLoginInputSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))


class ResetPasswordInputSchema(Schema):
    password = fields.Str(required=True, validate=validate.Length(min=6))