from flask import Blueprint, render_template, request, redirect, url_for, g, jsonify
from logto import LogtoException

from app import db, client
from app.blueprints.auth_logic import authenticated
from app.models import User

web_logic = Blueprint('web_logic', __name__)

@web_logic.route('/')
async def home():
    user_count = User.query.count()
    return render_template('landing.html', user=client.isAuthenticated(), num_users=user_count)

@web_logic.route('/dashboard')
@authenticated(shouldRedirect=True, fetchUserInfo=False)
async def dashboard():
    user_count = User.query.count()
    return render_template('dashboard.html', user=client.getIdTokenClaims(), num_users=user_count)

@web_logic.route('/manage')
@authenticated(shouldRedirect=True, fetchUserInfo=False)
async def manage_apps():
    return render_template('manage_apps.html', user=client.getIdTokenClaims())

@web_logic.route("/protected/userinfo")
@authenticated(shouldRedirect=True, fetchUserInfo=False)
async def protectedUserinfo():
    try:
        return (
            "<h2>User info</h2>"
            + g.user.model_dump_json(indent=2, exclude_unset=True).replace("\n", "<br>")
        )
    except LogtoException as e:
        return "<h2>Error</h2>" + str(e) + "<br>" + "<a href='/sign-out'>Sign out</a>"