from flask import Blueprint, render_template, request, redirect, url_for

from app import app
from app.blueprints.web_logic import web_logic
from app.blueprints.auth_logic import auth_logic
from app.blueprints.service_logic import service_logic

app.register_blueprint(web_logic)
app.register_blueprint(auth_logic)
app.register_blueprint(service_logic)

@app.errorhandler(Exception)
def handle_error(error):
    # Get the error code, default to 500 if not specified
    error_code = getattr(error, 'code', 500)
    error_message = getattr(error, 'description', 'An error occurred')
    return render_template("error.html", error_code=error_code, error_message=error_message), error_code
