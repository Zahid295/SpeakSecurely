from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from extensions import mongo

# User Model
class User(UserMixin):
    def __init__(self, username, password, _id=None):
        self.username = username
        self.password = password  # Changed from password_hash to password
        self._id = _id

    @staticmethod
    def create(username, password):
        hashed_password = generate_password_hash(password)
        user_id = mongo.db.Users.insert_one({  # Changed to 'Users' to match your collection name
            'username': username,
            'password': hashed_password  # Field name changed to 'password'
        }).inserted_id
        return User(username, hashed_password, user_id)

    @staticmethod
    def find_by_username(username):
        user_data = mongo.db.Users.find_one({'username': username})  # Changed to 'Users'
        if user_data:
            return User(username=user_data['username'], password=user_data['password'], _id=user_data['_id'])
        return None

    @staticmethod
    def get(user_id):
        user_data = mongo.db.Users.find_one({'_id': ObjectId(user_id)})  # Changed to 'Users'
        if user_data:
            return User(username=user_data['username'], password=user_data['password'], _id=user_data['_id'])
        return None

    def check_password(self, password):
        return check_password_hash(self.password, password)  # Changed from password_hash to password

    def get_id(self):
        return str(self._id)
    
    @property
    def is_active(self):
        """True, as all users are active."""
        return True

    @staticmethod
    def update(username, update_data):
        mongo.db.Users.update_one(  # Changed to 'Users'
            {'username': username},
            {'$set': update_data}
        )

    @staticmethod
    def delete(username):
        mongo.db.Users.delete_one({'username': username})  # Changed to 'Users'


# # Session Model
# class Session:
#     def __init__(self, user_id, session_id, data, created_at=None, updated_at=None):
#         self.user_id = user_id
#         self.session_id = session_id
#         self.data = data
#         self.created_at = created_at or datetime.utcnow()
#         self.updated_at = updated_at or datetime.utcnow()

#     @classmethod
#     def create(cls, user_id, session_data):
#         session_collection = current_app.mongo.db.sessions
#         session_id = session_collection.insert_one({
#             'user_id': user_id,
#             'data': session_data,
#             'created_at': datetime.now(timezone.utc),
#             'updated_at': datetime.now(timezone.utc)
#         }).inserted_id
#         return cls(user_id, session_id, session_data)
    
#     @classmethod
#     def find_by_session_id(cls, session_id):
#         session_collection = current_app.mongo.db.sessions
#         session_data = session_collection.find_one({'_id': session_id})
#         if session_data:
#             return cls(
#                 session_data['user_id'],
#                 session_data['_id'],
#                 session_data['data'],
#                 session_data['created_at'],
#                 session_data['updated_at']
#             )
#         return None

#     @classmethod
#     def update(cls, session_id, session_data):
#         session_collection = current_app.mongo.db.sessions
#         session_collection.update_one(
#             {'_id': session_id},
#             {'$set': {
#                 'data': session_data,
#                 'updated_at': datetime.now(timezone.utc)
#             }}
#         )
#     @classmethod
#     def delete(cls, session_id):
#         session_collection = current_app.mongo.db.sessions
#         session_collection.delete_one({'_id': session_id})