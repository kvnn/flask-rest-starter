from marshmallow import Schema, fields, validate


class TweetInput(Schema):
    body = fields.Str(required=True, validate=validate.Length(min=6, max=255))
    auth_token = fields.Str(required=True)
    parent_id = fields.Number(required=False)


class LikeInput(Schema):
    tweet_id = fields.Number(required=True)
    auth_token = fields.Str(required=True)