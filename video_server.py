import cv2
import time
import logging
from flask import Flask, Response
from threading import Lock

app = Flask(__name__)

_latest_frame = None
_lock = Lock()

def update_frame(frame):
    global _latest_frame
    with _lock:
        _latest_frame = frame.copy()

def _mjpeg_generator():
    while True:
        with _lock:
            frame = _latest_frame

        if frame is None:
            time.sleep(0.05)
            continue

        ok, jpg = cv2.imencode(".jpg", frame)
        if not ok:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            jpg.tobytes() +
            b"\r\n"
        )

@app.route("/video")
def video():
    return Response(
        _mjpeg_generator(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

def start_video_server():
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False,
        use_reloader=False,
        threaded=True
    )
