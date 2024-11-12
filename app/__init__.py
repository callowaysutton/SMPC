from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from logto import LogtoClient, LogtoConfig, Storage, LogtoClient, LogtoConfig, Storage, UserInfoScope
from flask import session
from typing import Union

import logging, os, random, docker

load_dotenv()

app = Flask(__name__)

logger = app.logger
logger.setLevel(logging.DEBUG)

if os.getenv('DATABASE_URI') is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
else:
    logger.log(logging.WARN, 'DATABASE_URI is not set in the environment variables. Assuming development environment, using SQLite.')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

# Set the app secret to a random set of 32 characterrs
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') if os.getenv('SECRET_KEY') is not None else ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=32))

db = SQLAlchemy(app)

class SessionStorage(Storage):
    def get(self, key: str) -> Union[str, None]:
        return session.get(key, None)

    def set(self, key: str, value: Union[str, None]) -> None:
        session[key] = value

    def delete(self, key: str) -> None:
        session.pop(key, None)

client = LogtoClient(
    LogtoConfig(
        endpoint=os.getenv("LOGTO_ENDPOINT"),
        appId=os.getenv("LOGTO_APP_ID"),
        appSecret=os.getenv("LOGTO_SECRET"),
        scopes=[
            UserInfoScope.email,
            UserInfoScope.organizations,
            UserInfoScope.organization_roles,
            UserInfoScope.custom_data,
            UserInfoScope.profile,
        ],  # Update scopes as needed
    ),
    storage=SessionStorage(),
)

# Check if the database connection is working
if db is not None:
    logger.log(logging.INFO, 'Connected to the database.')
else:
    logger.log(logging.INFO, 'Failed to connect to the database.')

docker_client = docker.from_env()

from app import routes, models

with app.app_context():
    db.create_all()