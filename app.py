# importing flask packages
import os
import atexit
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, make_response, session
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from flask_socketio import SocketIO, emit
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from dotenv import load_dotenv
from extensions import mongo
from flask_cors import CORS
from bson import ObjectId
import json
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timezone, timedelta
import bleach

# Clean inputs
def sanitize(input_string):
    return bleach.clean(input_string)


load_dotenv()


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
# CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app)
mongo.init_app(app)
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
        username = sanitize(request.form['username'])
        password = sanitize(request.form['password'])
        hashed_password = generate_password_hash(password)
        users.insert_one({'username': username, 'password': hashed_password})
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = sanitize(request.form['username'])
        password = sanitize(request.form['password'])
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
     user_messages = messages.find({
        '$or': [
            {'sender_id': ObjectId(user_id)},
            {'recipient_id': ObjectId(user_id)}
        ]
    })
    #  user_messages = messages.find({'recipient_id': ObjectId(user_id)})
     messages_list = []
     for message in user_messages:
        sender = users.find_one({'_id': message['sender_id']})
        if sender:
            message['sender'] = sender['username']  # Get sender's username
        else:
            message['sender'] = 'Unknown'  # Handle case where sender is not found
        messages_list.append(message)
     # Fetch list of all users except the current user
     contacts = users.find({'_id': {'$ne': ObjectId(user_id)}})

     # Convert MongoDB cursor to a list of dictionaries
     contacts_list = [contact for contact in contacts]

     return render_template('messages.html', messages=user_messages, contacts=contacts_list)

@app.route('/messages/<recipient_id>', methods=['GET'])
@login_required
def get_messages(recipient_id):
    sanitized_recipient_id = sanitize(recipient_id)

    if 'user_id' not in session:
        return make_response('Unauthorized', 401)
    # Assuming 'user_id' is stored in session when the user logs in
    user_id = session['user_id']
    user_messages = messages.find({
        '$or': [
            {'sender_id': ObjectId(user_id), 'recipient_id': ObjectId(sanitized_recipient_id)},
            {'sender_id': ObjectId(sanitized_recipient_id), 'recipient_id': ObjectId(user_id)}
        ]
    }).sort('timestamp', 1)
    # user_messages = messages.find({'recipient_id': ObjectId(user_id)})
    result = []
    for message in user_messages:
        sender = users.find_one({'_id': message['sender_id']})
        if sender:
            sender_username = sender['username']
        else:
            sender_username = 'Unknown'
        message_dict = {
            '_id': str(message['_id']),
            'sender': sender_username,
            'recipient_id': str(message['recipient_id']),
            'body': message['body'],
            'timestamp': message['timestamp']
        }
        result.append(message_dict)
    return jsonify(result)


@app.route('/send', methods=['POST'])
@login_required
def send_message():
    try:
        recipient_username = sanitize(request.form.get('recipient'))
        body = sanitize(request.form.get('message'))

        if not recipient_username or not body:

            return make_response('Bad Request', 400)
        
        recipient_user = users.find_one({'username': recipient_username})
        
        if not recipient_user:
            flash('Recipient user does not exist.')

            return redirect(url_for('index'))
        
        messages.insert_one({
            'sender_id': ObjectId(session['user_id']),
            'recipient_id': ObjectId(recipient_user['_id']),
            'body': body,
            'timestamp': datetime.now(timezone.utc)
        })

        return redirect(url_for('index'))
    
    except Exception as e:
        (f"Error in send_message: {e}")
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


# Function to delete messages older than one week
def delete_old_messages():
    one_week_ago = datetime.now(timezone.utc) - timedelta(weeks=1)
    messages.delete_many({'timestamp': {'$lt': one_week_ago}})

# Schedule the task
scheduler = BackgroundScheduler()
scheduler.add_job(delete_old_messages, 'interval', days=1)
scheduler.start()

# Ensure the scheduler shuts down when the app exits
atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    socketio.run(app, debug=True) 
