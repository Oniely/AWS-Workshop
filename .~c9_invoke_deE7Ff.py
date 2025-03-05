import json


def hello(event, context):
    body = {
        "message": "We are team Oniely and this is the hello world from lambda",
    }

    print("I added a pretty little print here for debugging")
    print(f"Events: {event}")

    response = {"statusCode": 200, "body": json.dumps(body)}

    return response
 