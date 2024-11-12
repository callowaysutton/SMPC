from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from dataclasses import dataclass
import uuid

from app import db

@dataclass
class User(db.Model):
    id: uuid.UUID
    email: str
    apps: Mapped['App']
    num_apps: int

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(120), unique=True, nullable=False)
    apps = db.relationship('App', backref='user', lazy=True)
    num_apps = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return '<User %r>' % self.username

@dataclass
class App(db.Model):
    id: uuid.UUID
    name: str
    icon: str
    description: str
    hostname: str
    docker_image: str
    port: int
    user_id: uuid.UUID
    containers: Mapped['DockerContainer']

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(80), unique=True, nullable=False)
    icon = db.Column(db.String(120), unique=True, nullable=True, default='/static/media/default.webp')
    description = db.Column(db.Text, unique=True, nullable=True)
    hostname = db.Column(db.String(120), unique=True, nullable=False)
    docker_image = db.Column(db.String(120), unique=True, nullable=False)
    port = db.Column(db.Integer, nullable=False)

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    containers = db.relationship('DockerContainer', backref='app', lazy=True)

    def __repr__(self):
        return '<App %r>' % self.name

@dataclass
class DockerContainer(db.Model):
    id: uuid.UUID
    container_id: str
    app_id: uuid.UUID

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    container_id = db.Column(db.Text, unique=True, nullable=False)
    app_id = db.Column(UUID(as_uuid=True), db.ForeignKey('app.id'), nullable=False)

    def __repr__(self):
        return '<DockerContainer %r>' % self.container_id