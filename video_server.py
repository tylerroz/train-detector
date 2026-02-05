import cv2
import time
import logging
from flask import Flask, Response
from threading import Lock

app = Flask(__name__)

_latest_frame = None
_latest_jpeg = None
_lock = Lock()

def update_frame(frame):
    global _latest_frame
    global _latest_jpeg
    with _lock:
        ok, jpg = cv2.imencode(
            ".jpg",
            frame,
            [cv2.IMWRITE_JPEG_QUALITY, 80]
        )
        if ok:
            _latest_jpeg = jpg.tobytes()

def _mjpeg_generator():
    while True:
        with _lock:
            jpg = _latest_jpeg

        if jpg is None:
            time.sleep(0.1)
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            jpg +
            b"\r\n"
        )

        # 1/ stream FPS (20)
        time.sleep(.05)

@app.route("/video")
def video():
    response = Response(
        _mjpeg_generator(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

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
