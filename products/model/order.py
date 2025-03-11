import boto3
from botocore.exceptions import ClientError
import os


ORDERS_TABLE = os.environ.get("ORDERS_TABLE")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(ORDERS_TABLE)


class Order:
    @staticmethod
    def save(order_id, product_id, quantity):
        try:
            existing_order = Order.get(order_id)

            if existing_order:
                print(f"Order with ID {order_id} already exists.")
                return {"error": "Order ID already exists."}

            product_table = dynamodb.Table(os.environ.get("PRODUCTS_TABLE"))
            product = product_table.get_item(Key={"product_id": product_id}).get("Item")

            table.put_item(
                Item={
                    "order_id": order_id,
                    "product_id": product_id,
                    "quantity": quantity,
                    "total": product["price"] * quantity,
                }
            )

            if not product:
                print(f"Product with ID {product_id} does not exist.")
                return {"error": "Product ID does not exist."}

            new_stock = product["quantity"] - quantity

            if new_stock < 0:
                print(f"Not enough stock for product ID {product_id}.")
                return {"error": "Not enough stock."}

            product_table.update_item(
                Key={"product_id": product_id},
                UpdateExpression="SET quantity = :new_stock",
                ExpressionAttributeValues={":new_stock": new_stock},
                ReturnValues="UPDATED_NEW",
            )

            return {
                "message": "Order saved successfully.",
                "total": product["price"] * quantity,
            }
        except ClientError as e:
            print(f"Error saving order: {e}")
            return {"error": "Failed to save order."}

    @staticmethod
    def get(order_id):
        try:
            response = table.get_item(Key={"order_id": order_id})
            return response.get("Item")
        except ClientError as e:
            print(f"Error retrieving order: {e}")
            return None

    @staticmethod
    def update(order_id, update_expression, expression_values):
        try:
            response = table.update_item(
                Key={"order_id": order_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues="UPDATED_NEW",
            )
            return response.get("Attributes")
        except ClientError as e:
            print(f"Error updating order: {e}")
            return {"error": "Failed to update order."}

    @staticmethod
    def delete(order_id):
        try:
            response = table.delete_item(Key={"order_id": order_id})
            return response
        except ClientError as e:
            print(f"Error deleting order: {e}")
            return {"error": "Failed to delete order."}
