from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from env import Config
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config.from_object(Config)

mongo = PyMongo(app)

# User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    mongo.db.users.insert_one({
        'username': data['username'],
        'password': hashed_password
    })
    return jsonify({'message': 'Registered successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)
