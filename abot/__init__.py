import os

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Inicia app de Flask y Middlewares
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

CORS(app)

app.debug = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../abot.db"
db = SQLAlchemy(app)

# Se cargan las rutas
from abot import routes
