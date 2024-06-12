from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)

load_dotenv()

app.config["MONGO_URI"] = os.getenv("DATABASE_URL")

mongo = PyMongo(app)
