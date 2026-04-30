import logging

from flask import Flask
from api.routes import api_bp
from api.device import device_bp

app = Flask(__name__)
app.register_blueprint(api_bp)
app.register_blueprint(device_bp)

def start_api_server():
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True
    )

if __name__ == "__main__":
    start_api_server()
