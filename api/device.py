from flask import Blueprint, jsonify

import subprocess

device_bp = Blueprint("device", __name__)

@device_bp.route("/api/device/temp")
def active():
    cmd = 'vcgencmd measure_temp | egrep -o \'[0-9]*\\.[0-9]*\''
    temp = float(subprocess.getoutput(cmd))
    result = {
        "temperature": temp,
        "unit": "C",
        "status": "ok" if temp <= 60 else ("warning" if temp <= 65 else "critical")
    }
    
    return jsonify(result)