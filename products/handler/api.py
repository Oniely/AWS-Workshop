import json
import boto3
from decimal import Decimal
from model.product import Product
import os


PRODUCT_TABLE = os.environ.get('PRODUCT_TABLE')

class DecimalEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Decimal):
      return str(obj)
    return json.JSONEncoder.default(self, obj)

def hello(event, context):
    body = {
        "message": "We are team Oniely and this is the hello world from lambda",
    }

    print("I added a pretty little print here for debugging")
    print(f"Events: {event}")

    response = {"statusCode": 200, "body": json.dumps(body)}

    return response
 
def get_all_products(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table(PRODUCT_TABLE)
    
    return_body = {}
    return_body["items"] = table.scan().get('Items')
    
    return_body["status"] = "success"
    response = {"statusCode": 200, "body": json.dumps(return_body, cls=DecimalEncoder)}
    
    return response
    
    
def create_one_product(event, context):
    body = json.loads(event.get("body", "{}"), parse_float=Decimal)
    product_id = body['product_id']
    
    if not body:
        return {"statusCode": 400, "body": json.dumps({"error": "Request body is required"})}
        
    if not product_id:
        return {'statusCode': 400, "body": json.dumps({'error': 'Required a Product ID'})}
        
    new_product = Product(product_id)
    
    product = new_product.save(body['product_name'], body['brand_name'], body['price'], body['quantity'])
    
    if not product:
        return {"statusCode": 400, "body": json.dumps({"error": "Something went wrong while adding product"})}
        
    
    response = {"statusCode": 200, "body": json.dumps(body, cls=DecimalEncoder)}
    
    # sqs queue 
    sqs = boto3.resource('sqs', region_name='us-east-2')
    queue = sqs.get_queue_by_name(QueueName='my-sqs-oniely')    
    response = queue.send_message(MessageBody=json.dumps(body, cls=DecimalEncoder))
    
    print(body)
    
    return body
 
def get_product(event, context):
    path_params = event.get("pathParameters", {})
    product_id = path_params.get("id")
    
    if not product_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Product ID is required"})}
    
    
    
    return_body = {}
    product = Product(product_id).get(product_id)
    
    if not product:
        return {"statusCode": 404, "body": json.dumps({"error": "Product not found"})}
    
    return_body['items'] = product
    response = {"statusCode": 200, "body": json.dumps(return_body, cls=DecimalEncoder)}
    
    return response
    
def delete_product(event, context):
    path_params = event.get("pathParameters", {})
    product_id = path_params.get("id")
    
    if not product_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Product ID is required"})}
    
    return_body = {}
    product = Product(product_id).delete()
    
    if not product:
        return {"statusCode": 404, "body": json.dumps({"message": "Product ID not found"})}
    
    return_body['items'] = product
    
    return_body['status'] = 'success'
    response = {"statusCode": 200, "body": json.dumps(return_body, cls=DecimalEncoder)}
    
    return response
    
    
def update_product(event, context):
    path_params = event.get("pathParameters", {})
    product_id = path_params.get("id")
    
    if not product_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Product ID is required"})}
    
    body = json.loads(event.get("body", "{}"), parse_float=Decimal)
    
    if not body:
        return {"statusCode": 400, "body": json.dumps({"error": "Request body is required"})}
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table(PRODUCT_TABLE)
    
    return_body = {}
    data = table.get_item(Key={'product_id': product_id})
    item = data.get('Item')
    
    if not item:
        return {"statusCode": 404, "body": json.dumps({"message": "Product ID not found"})}
        
    update_expression = "SET " + ", ".join(f"{key} = :{key}" for key in body.keys())
    expression_values = {f":{key}": value for key, value in body.items()}
    
    updated_product = Product(product_id).update(product_id, update_expression, expression_values)
    
    return_body['status'] = 'success'
    response = {"statusCode": 200, "body": json.dumps(updated_product, cls=DecimalEncoder)}
    
    return response