import boto3
from botocore.exceptions import ClientError
import os


PRODUCT_TABLE = os.environ.get('PRODUCT_TABLE')

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(PRODUCT_TABLE)

class Product:
    def __init__(self, product_id):
        self.product_id = product_id

    def save(self, product_name, brand_name, price, quantity):
        """ Save product to DynamoDB """
        try:
            table.put_item(
                Item={
                    "product_id": self.product_id,
                    "product_name": product_name,
                    "brand_name": brand_name,
                    "price": price,
                    "quantity": quantity,
                }
            )
            return True
        except ClientError as e:
            print(f"Error saving product: {e}")
            return False

    @staticmethod
    def get(product_id):
        """ Retrieve a product by ID """
        try:
            response = table.get_item(Key={"product_id": product_id})
            return response.get("Item")
        except ClientError as e:
            print(f"Error retrieving product: {e}")
            return None

    def delete(self):
        """ Delete a product """
        try:
            table.delete_item(Key={"product_id": self.product_id})
            return True
        except ClientError as e:
            print(f"Error deleting product: {e}")
            return False
            
    def update(self, product_id, update_expression, expression_value):
        """ Update a product """
        try:
            response = table.update_item(
                Key={"product_id": product_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_value,
                ReturnValues="ALL_NEW"
            )
            return response.get('Attributes')
        except ClientError as e:
            print(f"Error deleting product: {e}")
            return False
