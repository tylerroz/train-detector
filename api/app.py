import logging

from flask import Flask
from api.routes import api_bp

app = Flask(__name__)
app.register_blueprint(api_bp)

def start_api():
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host="127.0.0.1", port=5000)
