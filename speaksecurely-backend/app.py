# importing flask packages
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_pymongo import PyMongo
from itsdangerous import Serializer
# from itsdangerous.timed import TimestampSigner
from itsdangerous import URLSafeTimedSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from env import MONGO_URI
from models import User
import os

# flask instance
app = Flask(__name__)
app.config["MONGO_URI"] = MONGO_URI
app.config['SECRET_KEY'] = '956c04080ed8ad757ea18ab3fca9967'
socketio = SocketIO(app, cors_allowed_origins=['http://localhost:5000', 'http://127.0.0.1:5000'])


# CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


mongo = PyMongo(app)


@app.route('/')
def index():
    # Render home template
    return render_template('index.html')


@app.route('/chat')
def chat():
    return render_template('chat.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username': request.form['username']})

        if existing_user is None:
            hashed_password = generate_password_hash(request.form['password'])
            users.insert_one({
                'username': request.form['username'],
                'password': hashed_password
            })
            session['username'] = request.form['username']
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists')

    return render_template('register.html')


# User Registration
# @app.route('/register', methods=['POST'])
# def register():
#     print(mongo.db)
#     data = request.get_json()
#     hashed_password = generate_password_hash(data['password'])
#     mongo.db.Users.insert_one({
#         'username': data['username'],
#         'password': hashed_password
#     })
#     return jsonify({'message': 'Registered successfully'}), 201

# # User Login
# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     user = mongo.db.Users.find_one({'username': data['username']})
#     if user and check_password_hash(user['password'], data['password']):
#         # Generate a token with expiration
#         s = Serializer(app.config['SECRET_KEY'])
#         token = s.dumps({'user_id': str(user['_id'])})
#         return jsonify({'token': token}), 200
#     else:
#         return jsonify({'message': 'Invalid username or password'}), 401


# # User logout
# @app.route('/logout', methods=['POST'])
# def logout():
#     session.pop('username', None)
#     return jsonify({'message': 'Logged out successfully'}), 200

# Event handler for receiving messages
# @socketio.on('send_message')
# def handle_message(data):
#     print(f"Data received: {data}")
#     text = data.get('message', '')
#     emit('echo', {'echo': f'Server Says: {text}'}, broadcast=True, include_self=True)
@socketio.on('send_message')
def handle_message(data):
    print("send_message event triggered")
    message = data['message']
    print('received message: ' + message)
    emit('message_response', {'message': f'Server Says: {message}'}, broadcast=True, include_self=True)


if __name__ == '__main__':
    # Use socketio.run instead of app.run
    socketio.run(app, debug=True) 
