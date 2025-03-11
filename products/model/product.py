import boto3
from botocore.exceptions import ClientError
import os


PRODUCT_TABLE = os.environ.get('PRODUCT_TABLE')

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(PRODUCT_TABLE)

class Product:
    @staticmethod
    def save(product_id, product_name, brand_name, price, quantity):
        """ Save product to DynamoDB """
        try:
            response = table.scan(
                FilterExpression="product_id = :id OR product_name = :name",
                ExpressionAttributeValues={":id": product_id, ":name": product_name}
            )

            existing_product = response.get("Items", [])
            
            if existing_product:
                existing_product = existing_product[0]
            
                if existing_product["product_id"] == product_id:
                    print(f"Product with ID {product_id} already exists.")
                    return {"error": "Product ID already exists."}
                if existing_product["product_name"] == product_name:
                    print(f"Product with name '{product_name}' already exists.")
                    return {"error": "Product name already exists."}
            
            table.put_item(
                Item={
                    "product_id": product_id,
                    "product_name": product_name,
                    "brand_name": brand_name,
                    "price": price,
                    "quantity": quantity,
                }
            )
            return {"message": "Product saved successfully."}
        except ClientError as e:
            print(f"Error saving product: {e}")
            return {"error": "Failed to save product."}

    @staticmethod
    def get(product_id):
        """ Retrieve a product by ID """
        try:
            response = table.get_item(Key={"product_id": product_id})
            return response.get("Item")
        except ClientError as e:
            print(f"Error retrieving product: {e}")
            return None
            
    @staticmethod
    def get_by_name(product_name):
        """ Retrieve a product by ID """
        try:
            response = table.scan(
                FilterExpression="product_name = :name",
                ExpressionAttributeValues={":name": product_name}
            )
            
            return response.get('Items', [])
        except ClientError as e:
            print(f"Error retrieving product: {e}")
            return None
    
    @staticmethod
    def delete(product_id):
        """ Delete a product """
        try:
            table.delete_item(Key={"product_id": product_id})
            return True
        except ClientError as e:
            print(f"Error deleting product: {e}")
            return False
        
    @staticmethod
    def update(product_id, update_expression, expression_value):
        """ Update a product """
        try:
            existing_product = Product.get(product_id)
            
            if not existing_product:
                return {"error": "Product doesn't exist."}
                
            response = table.update_item(
                Key={"product_id": product_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_value,
                ReturnValues="ALL_NEW"
            )
            
            return response.get('Attributes')
        except ClientError as e:
            print(f"Error updating product: {e}")
            return {"error": e}
       
    @staticmethod     
    def buy_product(product_id):
        try:
            existing_product = Product.get(product_id)
            
            if not existing_product:
                return {"error": "Product doesn't exist."}
                
            return ""
        except ClientError as e:
            print(f'Error buting product: {e}')
            return {'error': e}
