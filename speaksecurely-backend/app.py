# importing flask packages
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from env import MONGO_URI
import os

# flask instance
app = Flask(__name__)
app.config["MONGO_URI"] = MONGO_URI
app.secret_key = app.config['SECRET_KEY']
socketio = SocketIO(app, cors_allowed_origins='*')

mongo = PyMongo(app)

# User Registration
@app.route('/register', methods=['POST'])
def register():
    print(mongo.db)
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'])
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

# User logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'message': 'Logged out successfully'}), 200

# Event handler for receiving messages
@socketio.on('send_message')
def handle_message(data):
    text = data.get('message', '').encode('ascii', 'ignore')
    emit('echo', {'echo': f'Server Says: {text}'}, broadcast=True, include_self=False)


if __name__ == '__main__':
    app.run(debug=True)
