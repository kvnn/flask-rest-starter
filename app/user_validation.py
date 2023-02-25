from marshmallow import Schema, fields, validate


class SignupInput(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    password2 = fields.Str(required=True, validate=validate.Length(min=6))


class LoginInput(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))


class PasswordInput(Schema):
    password = fields.Str(required=True, validate=validate.Length(min=6))