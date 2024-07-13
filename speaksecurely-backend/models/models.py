from datetime import datetime, timezone
from SpeakSecurely import db
from werkzeug.security import generate_password_hash, check_password_hash

# User Model
class User(db.Document):
    username = db.StringField(required=True, unique=True)
    password_hash = db.StringField(required=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Session Model
class Session(db.Document):
    user_id = db.ReferenceField('User')
    session_id = db.StringField(required=True, unique=True)
    data = db.DictField()
    created_at = db.DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = db.DateTimeField(default=lambda: datetime.now(timezone.utc))
