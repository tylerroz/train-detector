import logging

from flask import Flask
from api.routes import api_bp
from api.device import device_bp

app = Flask(__name__)
app.register_blueprint(api_bp)
app.register_blueprint(device_bp)

if __name__ == "__main__":
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(
        host="127.0.0.1", 
        port=5000
    )
