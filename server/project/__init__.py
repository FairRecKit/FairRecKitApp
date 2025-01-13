"""This package contains the fairreckit app server.

Packages:
    blueprints: contains the flask application objects (blueprints) used by fairreckit
    models: contains the models used to manipulate the server data.

methods:
    create_app
    register_blueprints
This program has been developed by students from the bachelor Computer Science at
Utrecht University within the Software Project course.
© Copyright Utrecht University (Department of Information and Computing Sciences)
"""
import sys
import logging
from flask import Flask
from flask_cors import CORS

from .models.result_storage import create_results_overview
from .models.mail import MailSender
from .models import make_mail
from .blueprints import experiment_bp, music_detail_bp, result_bp, results_bp


def create_app():
    """Instantiate the app."""
    app = Flask(__name__)
    app.config['ENV'] = 'development'
    app.config['DEBUG'] = True
    app.config['TESTING'] = False

    # Mail stuff
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'fairreckit@gmail.com'
    app.config['MAIL_PASSWORD'] = 'shxvajwlrlszpnaa'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    # Enable Cross-Origin Resource Sharing.
    CORS(app)

    # Add console output to log
    logger = logging.getLogger('logger')
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    # Route: root.
    @app.route('/')
    def home():
        return "Welcome to the Flask API!"

    # Route: Main.
    @app.route('/api/', methods=['GET'])
    def main():
        return {"msg":"Server online."}

    # Route: Do a sanity check.
    @app.route('/api/greeting', methods=['GET'])
    def greet():
        return {"greeting":"Greetings from the backend :)"}

    register_blueprints(app)
    create_results_overview()
    make_mail(app)
    return app


def register_blueprints(app):
    """
    Register Flask blueprints with routes.

    Args:
         app: the main app
    """
    app.register_blueprint(experiment_bp.blueprint)
    app.register_blueprint(result_bp.blueprint)
    app.register_blueprint(results_bp.blueprint)
    app.register_blueprint(music_detail_bp.blueprint)
