from marshmallow import Schema, fields, validate


class TweetInput(Schema):
    body = fields.Str(required=True, validate=validate.Length(min=6, max=255))
    auth_token = fields.Str(required=True)