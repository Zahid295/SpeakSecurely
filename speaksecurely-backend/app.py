# importing flask packages
from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_socketio import SocketIO, emit
# from flask_pymongo import PyMongo
# from itsdangerous import Serializer
# from itsdangerous.timed import TimestampSigner
# from itsdangerous import URLSafeTimedSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from env import MONGO_URI
from extensions import mongo

# flask instance
app = Flask(__name__)
app.config["MONGO_URI"] = MONGO_URI
mongo.init_app(app)
app.config['SECRET_KEY'] = '956c04080ed8ad757ea18ab3fca9967'
socketio = SocketIO(app, cors_allowed_origins=['http://localhost:5000', 'http://127.0.0.1:5000'])


from models.models import User
# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'routes_blueprint.login'

routes_blueprint = Blueprint('routes_blueprint', __name__)


# User loader callback
@login_manager.user_loader
def load_user(user_id):
    # Assuming User.get(user_id) fetches the user from the database
    return User.get(user_id)


@routes_blueprint.route('/')
def index():
    # Render home template
    return render_template('index.html')


@routes_blueprint.route('/chat')
@login_required
def chat():
    return render_template('chat.html')


@routes_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = mongo.db.Users  # Make sure this matches the collection name
        existing_user = users.find_one({'username': request.form['username']})

        if existing_user is None:
            hashed_password = generate_password_hash(request.form['password'])
            users.insert_one({
                'username': request.form['username'],
                'password': hashed_password
            })
            flash('Account created successfully!', 'success')
            return redirect(url_for('routes_blueprint.login'))
        else:
            flash('Username already exists')

    return render_template('register.html')


@routes_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.find_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            flash('You were successfully logged in', 'success')
            return redirect(url_for('routes_blueprint.chat'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')


@routes_blueprint.route('/logout')
def logout():
    logout_user()
    flash('You were logged out', 'success')
    return redirect(url_for('routes_blueprint.index'))


app.register_blueprint(routes_blueprint, url_prefix='/')



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
    socketio.run(app, debug=True) 
