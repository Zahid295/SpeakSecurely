# importing flask packages
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_pymongo import PyMongo
from itsdangerous import Serializer
# from itsdangerous.timed import TimestampSigner
from itsdangerous import URLSafeTimedSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from env import MONGO_URI
import os

# flask instance
app = Flask(__name__)
app.config["MONGO_URI"] = MONGO_URI
app.config['SECRET_KEY'] = '956c04080ed8ad757ea18ab3fca9967'
socketio = SocketIO(app, cors_allowed_origins='http://localhost:3000')


CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

mongo = PyMongo(app)


@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the Flask server!'}), 200

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
    if user and check_password_hash(user['password'], data['password']):
        # Generate a token with expiration
        s = Serializer(app.config['SECRET_KEY'])
        token = s.dumps({'user_id': str(user['_id'])})
        return jsonify({'token': token}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401


# User logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'message': 'Logged out successfully'}), 200

# Event handler for receiving messages
# @socketio.on('send_message')
# def handle_message(data):
#     print(f"Data received: {data}")
#     text = data.get('message', '')
#     emit('echo', {'echo': f'Server Says: {text}'}, broadcast=True, include_self=True)
@socketio.on('send_message')
def handle_message(data):
    try:
        print(f"Data received: {data}")  # Attempt to log all data received
        text = data.get('message', '')
        emit('echo', {'echo': f'Server Says: {text}'}, broadcast=True, include_self=True)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    # Use socketio.run instead of app.run
    socketio.run(app, debug=True) 
