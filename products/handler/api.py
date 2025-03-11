import json
import boto3
from decimal import Decimal
from model.product import Product
import os


PRODUCTS_TABLE = os.environ.get("PRODUCTS_TABLE")


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def hello(event, context):
    body = {
        "message": "We are team Oniely and this is the hello world from lambdas",
    }

    print("I added a pretty little print here for debugging")
    print(f"Events: {event}")

    response = {"statusCode": 200, "body": json.dumps(body)}

    return response


def get_all_products(event, context):
    dynamodb = boto3.resource("dynamodb", region_name="us-east-2")
    table = dynamodb.Table(PRODUCTS_TABLE)

    return_body = {}
    return_body["items"] = table.scan().get("Items")

    return_body["status"] = "success"
    response = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(return_body, cls=DecimalEncoder),
    }

    return response


def create_one_product(event, context):
    body = json.loads(event.get("body", "{}"), parse_float=Decimal)
    product_id = body["product_id"]

    if not body:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Request body is required"}),
        }

    if not product_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Required a Product ID"}),
        }

    product = Product()

    new_product_response = product.save(
        product_id,
        body["product_name"],
        body["brand_name"],
        body["price"],
        body["quantity"],
    )

    if "error" in new_product_response:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": new_product_response["error"]}),
        }

    return_body = {}
    return_body["items"] = body

    if "message" in new_product_response:
        return_body["message"] = new_product_response["message"]

    response = {"statusCode": 200, "body": json.dumps(return_body, cls=DecimalEncoder)}

    # sqs queue
    sqs = boto3.resource("sqs", region_name="us-east-2")
    queue = sqs.get_queue_by_name(QueueName="my-sqs-oniely")
    queue.send_message(MessageBody=json.dumps(body, cls=DecimalEncoder))

    print(return_body)

    return response


def get_product(event, context):
    path_params = event.get("pathParameters", {})
    product_id = path_params.get("id")

    if not product_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Product ID is required"}),
        }

    return_body = {}
    product = Product().get(product_id)

    if not product:
        return {"statusCode": 404, "body": json.dumps({"error": "Product not found"})}

    return_body["items"] = product
    response = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(return_body, cls=DecimalEncoder),
    }

    return response


def delete_product(event, context):
    path_params = event.get("pathParameters", {})
    product_id = path_params.get("id")

    if not product_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Product ID is required"}),
        }

    return_body = {}
    delete_product_response = Product().delete(product_id)

    if not delete_product_response:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Product deletion failed."}),
        }

    return_body["status"] = "success"
    response = {"statusCode": 200, "body": json.dumps(return_body, cls=DecimalEncoder)}

    return response


def update_product(event, context):
    path_params = event.get("pathParameters", {})
    product_id = path_params.get("id")

    if not product_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Product ID is required"}),
        }

    body = json.loads(event.get("body", "{}"), parse_float=Decimal)

    if not body:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Request body is required"}),
        }

    dynamodb = boto3.resource("dynamodb", region_name="us-east-2")
    table = dynamodb.Table(PRODUCTS_TABLE)

    return_body = {}
    data = table.get_item(Key={"product_id": product_id})
    item = data.get("Item")

    if not item:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "Product ID not found"}),
        }

    update_expression = "SET " + ", ".join(f"{key} = :{key}" for key in body.keys())
    expression_values = {f":{key}": value for key, value in body.items()}

    updated_product = Product().update(product_id, update_expression, expression_values)

    if "error" in updated_product:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": updated_product["error"]}),
        }

    return_body["status"] = "success"
    response = {
        "statusCode": 200,
        "body": json.dumps(updated_product, cls=DecimalEncoder),
    }

    return response


def get_product_by_name(event, context):
    path_params = event.get("pathParameters", {})
    product_name = path_params.get("name")

    print(product_name)

    if not product_name:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Product name is required"}),
        }

    return_body = {}
    product = Product().get_by_name(product_name)

    if not product:
        return {"statusCode": 404, "body": json.dumps({"error": "Product not found"})}

    return_body["items"] = product[0]
    response = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(return_body, cls=DecimalEncoder),
    }

    return response
