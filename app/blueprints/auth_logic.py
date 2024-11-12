from flask import Blueprint, request, redirect, jsonify, g, flash
from functools import wraps

from app import client, db
from app.models import User

import os

auth_logic = Blueprint('auth_logic', __name__)

@auth_logic.route("/callback")
async def callback():
    try:
        await client.handleSignInCallback(request.url) # Handle a lot of stuff

        # Check if the user's email ends with '.edu'
        if not client.getIdTokenClaims().email.endswith(".edu"):
            flash("You need an email that ends with '.edu' to sign in.")
            return redirect("/sign-out")

        # Check if the user is in the database
        user = User.query.filter_by(email=client.getIdTokenClaims().email).first()
        if user is None:
            # Add the user to the database
            user = User(email=client.getIdTokenClaims().email)
            db.session.add(user)

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash(str(e))
                return redirect("/sign-out")
        else:
            flash("Welcome back!")
        return redirect("/") # Redirect the user to the home page after a successful sign-in
    except Exception as e:
        # Change this to your error handling logic
        flash("Error: " + str(e))
        return redirect("/sign-out")

@auth_logic.route("/sign-in")
async def sign_in():
    # Get the sign-in URL and redirect the user to it
    return redirect(await client.signIn(
        redirectUri="http://localhost:5000/callback" if os.getenv("FLASK_ENV") != "production" else "https://social.iu.run/callback",
    ))

@auth_logic.route("/sign-out")
async def sign_out():
    flash("You have been signed out.")
    return redirect(
        # Redirect the user to the home page after a successful sign-out
        await client.signOut(postLogoutRedirectUri="http://localhost:5000/" if os.getenv("FLASK_ENV") != "production" else "https://social.iu.run/")
    )

def authenticated(shouldRedirect: bool = False, fetchUserInfo: bool = False):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if client.isAuthenticated() is False:
                if shouldRedirect:
                    return redirect("/sign-in")
                return jsonify({"error": "Not authenticated"}), 401

            # Store user info in Flask application context
            g.user = (
                await client.fetchUserInfo()
                if fetchUserInfo
                else client.getIdTokenClaims()
            )
            return await func(*args, **kwargs)

        return wrapper

    return decorator