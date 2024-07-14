from datetime import datetime, timezone
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash

# User Model
class User:
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

    @staticmethod
    def create(username, password):
        hashed_password = generate_password_hash(password)
        user_collection = current_app.mongo.db.users
        user_collection.insert_one({
            'username': username,
            'password': hashed_password
        })

    @staticmethod
    def find_by_username(username):
        user_collection = current_app.mongo.db.users
        return user_collection.find_one({'username': username})

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

    @staticmethod
    def update(username, update_data):
        user_collection = current_app.mongo.db.users
        user_collection.update_one(
            {'username': username},
            {'$set': update_data}
        )

    @staticmethod
    def delete(username):
        user_collection = current_app.mongo.db.users
        user_collection.delete_one({'username': username})


# Session Model
class Session:
    def __init__(self, user_id, session_id, data, created_at=None, updated_at=None):
        self.user_id = user_id
        self.session_id = session_id
        self.data = data
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(cls, user_id, session_data):
        session_collection = current_app.mongo.db.sessions
        session_id = session_collection.insert_one({
            'user_id': user_id,
            'data': session_data,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }).inserted_id
        return cls(user_id, session_id, session_data)
    
    @classmethod
    def find_by_session_id(cls, session_id):
        session_collection = current_app.mongo.db.sessions
        session_data = session_collection.find_one({'_id': session_id})
        if session_data:
            return cls(
                session_data['user_id'],
                session_data['_id'],
                session_data['data'],
                session_data['created_at'],
                session_data['updated_at']
            )
        return None

    @classmethod
    def update(cls, session_id, session_data):
        session_collection = current_app.mongo.db.sessions
        session_collection.update_one(
            {'_id': session_id},
            {'$set': {
                'data': session_data,
                'updated_at': datetime.now(timezone.utc)
            }}
        )
    @classmethod
    def delete(cls, session_id):
        session_collection = current_app.mongo.db.sessions
        session_collection.delete_one({'_id': session_id})