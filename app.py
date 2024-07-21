# importing flask packages
import os
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, make_response, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_socketio import SocketIO, emit, disconnect, join_room, leave_room
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
# from env import MONGO_URI
from dotenv import load_dotenv
from extensions import mongo
import logging
from flask_cors import CORS
from bson import ObjectId
import json


load_dotenv()

# Load environment variables from env.py if it exists
# try:
#     from env import MONGO_URI, SECRET_KEY
# except ImportError:
#     MONGO_URI = os.getenv('MONGO_URI')
#     SECRET_KEY = os.getenv('SECRET_KEY')

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)  # Convert ObjectId to string
        return super().default(obj)

# flask instance
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')


app.json_encoder = CustomJSONEncoder
CORS(app, resources={r"/*": {"origins": "*"}})
mongo.init_app(app)
# socketio = SocketIO(app, cors_allowed_origins=['http://localhost:5000', 'http://127.0.0.1:5000'])
socketio = SocketIO(app, cors_allowed_origins="*")


# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id


# User loader callback
@login_manager.user_loader
def load_user(user_id):
    user = users.find_one({'_id': ObjectId(user_id)})
    if user:
        return User(str(user['_id']))
    return None


users = mongo.db.Users
messages = mongo.db.messages

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        users.insert_one({'username': username, 'password': hashed_password})
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            user_obj = User(str(user['_id']))
            login_user(user_obj)
            session['user_id'] = str(user['_id'])
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
     if 'user_id' not in session:
        return redirect(url_for('login'))
     user_id = session['user_id']
     user_messages = messages.find({'recipient_id': ObjectId(user_id)})
     messages_list = []
     for message in user_messages:
        sender = users.find_one({'_id': message['sender_id']})
        logging.debug(f"Sender ID: {message['sender_id']}, Sender: {sender}")
        if sender:
            message['sender'] = sender['username']  # Get sender's username
        else:
            message['sender'] = 'Unknown'  # Handle case where sender is not found
        messages_list.append(message)
     return render_template('messages.html', messages=user_messages)

@app.route('/messages', methods=['GET'])
@login_required
def get_messages():
    if 'user_id' not in session:
        return make_response('Unauthorized', 401)
    # Assuming 'user_id' is stored in session when the user logs in
    user_id = session['user_id']
    user_messages = messages.find({'recipient_id': ObjectId(user_id)})
    result = []
    for message in user_messages:
        sender = users.find_one({'_id': message['sender_id']})
        if sender:
            sender_username = sender['username']
        else:
            sender_username = 'Unknown'
            logging.warning(f"Sender with ID {sender} not found.")
        message_dict = {
            '_id': str(message['_id']),
            'sender': sender_username,
            'recipient_id': str(message['recipient_id']),
            'body': message['body']
        }
        result.append(message_dict)
    return jsonify(result)


# Set up logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/send', methods=['POST'])
@login_required
def send_message():
    try:
        recipient_username = request.form.get('recipient')
        body = request.form.get('message')
        
        logging.debug(f"Recipient Username: {recipient_username}")
        logging.debug(f"Message Body: {body}")

        if not recipient_username or not body:
            logging.error("Recipient username or message body is missing.")
            return make_response('Bad Request', 400)
        
        recipient_user = users.find_one({'username': recipient_username})
        
        if not recipient_user:
            flash('Recipient user does not exist.')
            logging.error("Recipient user does not exist.")
            return redirect(url_for('index'))
        
        messages.insert_one({
            'sender_id': ObjectId(session['user_id']),
            'recipient_id': ObjectId(recipient_user['_id']),
            'body': body
        })
        logging.info("Message sent successfully.")
        return redirect(url_for('index'))
    
    except Exception as e:
        logging.error(f"Error in send_message: {e}")
        return make_response('Internal Server Error', 500)
    

# SocketIO event handler
@socketio.on('connect')
def handle_connect():
    user_id = session.get('user_id')
    if user_id:
        socket_id = request.sid
        users.update_one({'_id': ObjectId(user_id)}, {'$set': {'socket_id': socket_id}})
        emit('status', {'message': 'Connected', 'user_id': user_id})

@socketio.on('disconnect')
def handle_disconnect():
    user_id = session.get('user_id')
    if user_id:
        users.update_one({'_id': ObjectId(user_id)}, {'$unset': {'socket_id': ''}})
        emit('status', {'message': 'Disconnected', 'user_id': user_id})


if __name__ == '__main__':
    socketio.run(app, debug=True) 
