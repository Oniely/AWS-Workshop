import boto3
import uuid
from datetime import datetime
import os

USERS_TABLE = os.environ.get("USERS_TABLE")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(USERS_TABLE)


class User:
    def __init__(self, user_id=None, username=None, email=None):
        self.user_id = user_id
        self.username = username
        self.email = email

    @staticmethod
    def get_user(email):
        try:
            response = table.scan(
                FilterExpression="email = :email",
                ExpressionAttributeValues={":email": email},
            )
            existing_user = response.get("Items", [])

            if existing_user[0]:
                return existing_user[0]
            else:
                return None
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None

    def login_user(self, email, password):
        try:
            existing_user = User.get_user(email)

            if not existing_user:
                raise ValueError("User not found")

            if existing_user.get("password") == password:
                return {
                    "user_id": existing_user.get("user_id"),
                    "email": existing_user.get("email"),
                }
            else:
                raise ValueError("Email or password is incorrect")

        except ValueError as e:
            return {"error": str(e)}
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return {"error": "Something went wrong while logging in"}

    def create_user(self, email, password, confirmPassword):
        try:
            if not email or not password or "@" not in email:
                raise ValueError("Valid email and password are required")

            if len(password) < 6:
                raise ValueError("Password must be at least 6 characters")

            if password != confirmPassword:
                raise ValueError("Passwords do not match")

            existing_user = User.get_user(email)
            if existing_user:
                raise ValueError("User with this email already exists")

            user_id = str(uuid.uuid4())
            current_time = datetime.now().isoformat()

            new_user = {
                "user_id": user_id,
                "email": email,
                "password": password,
                "created_at": current_time,
                "updated_at": current_time,
            }

            table.put_item(Item=new_user)

            user_response = new_user.copy()
            user_response.pop("password")
            return user_response

        except ValueError as e:
            return {"error": str(e)}
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return {"error": "Failed to create user"}
