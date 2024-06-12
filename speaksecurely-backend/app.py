from flask import Flask
from flask_pymongo import PyMongo
from env import Config
import os

app = Flask(__name__)
app.config.from_object(Config)


mongo = PyMongo(app)

if __name__ == '__main__':
    app.run(debug=True)
