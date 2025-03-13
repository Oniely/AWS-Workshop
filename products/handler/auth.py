import json
from model.user import User


def login_user(event, context):
    body = json.loads(event.get("body", "{}"))

    response = {}

    if not body.get("email") or not body.get("password"):
        response = {
            "statusCode": 400,
            "body": json.dumps({"error": "Email and password are required"}),
        }
        return response

    response = User().login_user(body.get("email"), body.get("password"))

    return response


def register_user(event, context):
    body = json.loads(event.get("body", "{}"))

    response = {}

    if (
        not body.get("email")
        or not body.get("password")
        or not body.get("confirmPassword")
    ):
        response = {
            "statusCode": 400,
            "body": json.dumps({"error": "Email and password are required"}),
        }
        return response

    if body.get("password") != body.get("confirmPassword"):
        response = {
            "statusCode": 400,
            "body": json.dumps({"error": "Password do not match"}),
        }
        return response

    response = User().create_user(
        body.get("email"), body.get("password"), body.get("confirmPassword")
    )

    return response
