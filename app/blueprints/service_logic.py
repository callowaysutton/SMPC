from flask import Blueprint, render_template, request, redirect, url_for, g, jsonify
from tqdm import tqdm

from app import app, db, docker_client, client
from app.blueprints.auth_logic import authenticated
from app.models import App, User, DockerContainer

import signal, atexit

service_logic = Blueprint('service_logic', __name__)

@service_logic.route('/add_service', methods=['POST'])
@authenticated(shouldRedirect=True, fetchUserInfo=False)
async def add_service():
    # Get the name, hostname, docker_image, and port from the request body
    name = request.json.get('name')
    icon = request.json.get('icon')
    description = request.json.get('description')
    hostname = request.json.get('hostname')
    docker_image = request.json.get('docker_image')
    port = request.json.get('port')

    # Make sure they are all under 120 characters, not empty, unique and contain only alphanumeric characters
    if not name or len(name) > 120 or not any(char.isalnum() or char in '/._- ' for char in name):
        return jsonify({'error': 'Invalid name'}), 400
    if not hostname or len(hostname) > 120 or not hostname.isalnum():
        return jsonify({'error': 'Invalid hostname'}), 400
    if not docker_image or len(docker_image) > 120 or not any(char.isalnum() or char in '/.:_-' for char in docker_image):
        return jsonify({'error': 'Invalid docker_image'}), 400
    if not port or not port.isdigit():
        return jsonify({'error': 'Invalid port'}), 400
    
    # Check to see if the icon and description are valid, the icon should only include URL safe characters, which means '/', '.', '_', and '-' w/ all alphanumeric characters
    if icon and (len(icon) > 120 or not any(char.isalnum() or char in '/._-' for char in icon)):
        return jsonify({'error': 'Invalid icon'}), 400
    
    if description and any(char.isalnum() or char in '/._-&!@#$%^&* ' for char in icon):
        return jsonify({'error': 'Invalid description'}), 400
    
    # Get the user_id from the authenticated user's email
    user_id = User.query.filter_by(email=client.getIdTokenClaims().email).first().id
    
    # Make the App object
    app = App(name=name, icon=icon, description=description, hostname=hostname, docker_image=docker_image, port=int(port), user_id=user_id)

    # Add the app to the database
    db.session.add(app)

    # Commit the changes
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    
    # Modify the User object to increase the number of apps
    user = User.query.filter_by(id=user_id).first()
    user.num_apps += 1

    # Commit the changes
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    
    # Run the Docker container for the app and return the container ID, set the Caddy labels so that Caddy can reverse proxy to the container
    try:
        container = docker_client.containers.run(
            docker_image,
            detach=True,
            labels={
                'caddy': f"{hostname}-social.iu.run",
                'caddy.reverse_proxy': '{{upstreams ' + str(port) + '}}'
            },
            network='caddy',
            cpus=8,
            mem_limit='32g'
        )
    except Exception as e:
        db.session.delete(app)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
        return jsonify({'error': str(e)}), 400
    
    # Add the container to the database
    docker_container = DockerContainer(container_id=container.id, app_id=app.id)
    db.session.add(docker_container)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    
    return jsonify({'container_id': container.id}), 200

@service_logic.route('/stop_container', methods=['POST'])
@authenticated(shouldRedirect=True, fetchUserInfo=False)
async def stop_container():
    # Get the container_id from the request body
    container_id = request.json.get('container_id')

    # Check to see if the container exists
    container = DockerContainer.query.filter_by(container_id=container_id).first()
    if not container:
    # Stop the container
        try:
            docker_client.containers.get(container_id).remove(v=True, force=True)
        except Exception as e:
            return jsonify({'message': 'Tried to stop container, but no container was running...'}), 200
        return jsonify({'message': 'Container not in database, succesfully stopped rogue container'}), 200
    
    # Stop the container
    try:
        docker_client.containers.get(container_id).remove(v=True, force=True)
    except Exception as e:
        # Remove the container from the database since it is not running
        db.session.delete(container)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
        return jsonify({'error': str(e)}), 400
    
    # Remove the container from the database
    db.session.delete(container)

    # Commit the changes
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    
    return jsonify({'message': 'Container stopped'}), 200

@service_logic.route('/start_container', methods=['POST'])
@authenticated(shouldRedirect=True, fetchUserInfo=False)
async def start_container():
    # Get the app_id from the request body
    app_id = request.json.get('app_id')

    # Check to see if the app exists
    app = App.query.filter_by(id=app_id).first()

    if not app:
        return jsonify({'error': 'App not found'}), 404
    
    # Get the user_id from the authenticated user's email
    user_id = User.query.filter_by(email=client.getIdTokenClaims().email).first().id

    # Make sure the user owns the app
    if app.user_id != user_id:
        return jsonify({'error': 'You do not own this app'}), 401
    
    # Make sure no other containers are running for this app
    container = DockerContainer.query.filter_by(app_id=app_id).first()
    if container:
        return jsonify({'error': 'Container already running'}), 400
    
    try:
        container = docker_client.containers.run(
            app.docker_image,
            detach=True,
            labels={
                'caddy': f"{app.hostname}-social.iu.run",
                'caddy.reverse_proxy': '{{upstreams ' + str(app.port) + '}}'
            },
            network='caddy',
            cpus=8,
            mem_limit='32g'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    # Add the container to the database
    docker_container = DockerContainer(container_id=container.id, app_id=app.id)
    db.session.add(docker_container)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    
    return jsonify({'container_id': container.id}), 200

@service_logic.route('/remove_app', methods=['POST'])
@authenticated(shouldRedirect=True, fetchUserInfo=False)
async def remove_app():
    # Get the app_id from the request body
    app_id = request.json.get('app_id')

    # Check to see if the app exists
    app = App.query.filter_by(id=app_id).first()
    if not app:
        return jsonify({'error': 'App not found'}), 404
    
    # Get the user_id from the authenticated user's email
    user_id = User.query.filter_by(email=client.getIdTokenClaims().email).first().id

    # Make sure the user owns the app
    if app.user_id != user_id:
        return jsonify({'error': 'You do not own this app'}), 401
    
    # Get the Docker container for the app
    container = DockerContainer.query.filter_by(app_id=app_id).first()

    # Stop the container
    if container:
        try:
            docker_client.containers.get(container.container_id).remove(v=True, force=True)
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    # Remove the container from the database
    db.session.delete(container)

    # Remove the app from the database
    db.session.delete(app)

    # Commit the changes
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    
    return jsonify({'message': 'App removed'}), 200

@service_logic.route('/get_apps', methods=['GET'])
@authenticated(shouldRedirect=True, fetchUserInfo=False)
async def get_apps():
    # Get the user_id from the authenticated user's email
    user_id = User.query.filter_by(email=client.getIdTokenClaims().email).first().id

    # Get the apps that the user owns
    apps = App.query.filter_by(user_id=user_id).all()

    # Return the apps
    return jsonify(apps), 200

def shutdown_containers():
    # Check to see if there are any live containers from the database
    with app.app_context():
        containers = DockerContainer.query.all()
        if containers:
            print("\nShutting down containers...")
            for container in tqdm(containers, desc="Stopping containers", unit="container"):
                try:
                    # Forcefully stop and remove the container
                    docker_client.containers.get(container.container_id).remove(v=True, force=True)

                    # Remove the container from the database
                    db.session.delete(container)
                    
                    # Commit the changes
                    db.session.commit()
                except Exception as e:
                    print(f"Error stopping container {container.id}: {e}")

# Signal handler for graceful shutdown on app termination
def signal_handler(sig, frame):
    shutdown_containers()
    exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Ensure shutdown_containers runs on exit
atexit.register(shutdown_containers)