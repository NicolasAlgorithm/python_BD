class User:
    def __init__(self, user_id, username, password, email):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email

class UserManager:
    def __init__(self):
        self.users = []

    def create_user(self, username, password, email):
        user_id = len(self.users) + 1
        new_user = User(user_id, username, password, email)
        self.users.append(new_user)
        return new_user

    def read_user(self, user_id):
        for user in self.users:
            if user.user_id == user_id:
                return user
        return None

    def update_user(self, user_id, username=None, password=None, email=None):
        user = self.read_user(user_id)
        if user:
            if username:
                user.username = username
            if password:
                user.password = password
            if email:
                user.email = email
            return user
        return None

    def delete_user(self, user_id):
        user = self.read_user(user_id)
        if user:
            self.users.remove(user)
            return True
        return False

    def list_users(self):
        return self.users