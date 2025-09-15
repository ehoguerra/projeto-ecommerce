from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager

roles = ['admin', 'manager', 'employee']

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
