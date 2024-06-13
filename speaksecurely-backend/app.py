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
    mongo.db.Users.insert_one({
        'username': data['username'],
        'password': hashed_password
    })
    return jsonify({'message': 'Registered successfully'}), 201

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = mongo.db.Users.find_one({'username': data['username']})
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'message': 'Invalid username or password'}), 401
    return jsonify({'message': 'Logged in successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
