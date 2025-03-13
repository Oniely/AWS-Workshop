import uuid


class User:
    def __init__(self, user_id=None, username=None, email=None):
        self.user_id = user_id
        self.username = username
        self.email = email

    def get_user(self, email):
        # use self.user_id to fetch user from database
        pass

    def create_user(self):
        # generate a user_id and save user to database
        new_user_id = str(uuid.uuid4())
        pass
