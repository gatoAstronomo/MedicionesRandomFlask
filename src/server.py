from flask import Flask, request, jsonify
from flask_pymongo import PyMongo

FLASK_PORT = 8081
MONGO_URL = "mongodb://localhost:27017/pythonmongodb"

app = Flask(__name__)
app.config["MONGO_URI"] = MONGO_URL
mongo = PyMongo(app)

print("probando el servidor")