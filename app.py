from flask import Flask, send_file, request
import json

from src.modules.camera_manager import CameraManager
from src.modules.config_handler import ConfigHandler
from src.modules.capture_handler import CaptureHandler

app = Flask(__name__)

camera_manager = CameraManager()
camera_capture = CaptureHandler(camera_manager)
config_handler = ConfigHandler(camera_manager)

config = {
    'iso': None,
    'aperture': None,
    'shutterspeed': None,
    'whitebalance': None
}


@app.route('/api/connect')
def connect_to_cam():
    global config
    result = camera_manager.connect()
    config = config_handler.get_multiple_config_values(config)
    result["config"] = config
    return json.dumps(result)


@app.route('/api/disconnect')
def disconnect_from_cam():
    result = camera_manager.disconnect_camera()
    return json.dumps(result)


@app.route('/api/reset')
def reset_camera():
    result = camera_manager.reset_camera()
    return json.dumps(result)


@app.route('/api/status')
def status_connection():
    return json.dumps({"status": camera_manager.is_connected})


@app.route('/api/summary')
def summary_camera():
    result = camera_manager.get_camera_summary()
    return result


@app.route('/api/test')
def test_camera():
    if camera_manager.is_connected and camera_capture.wait_until_ready():
        result = camera_capture.capture_preview()
        return json.dumps({"status": "success", "message": "Photo captured successfully."})
    else:
        return json.dumps({"status": "error", "message": "Camera is not connected."})


@app.route('/api/capture')
def capture_photo():
    global result
    if camera_manager.is_connected and camera_capture.wait_until_ready():
        result = camera_capture.capture_image()
        return json.dumps({"status": "success", "message": "Photo captured successfully."})
    else:
        return json.dumps({"status": "error", "message": "Camera is not connected."})

@app.route('/api/get_photos')
def get_photos():
    global result
    try:
        path = result["data"]["save_path"]
        return send_file(path_or_file=path, mimetype="image/jpeg")
    except Exception as e:
        return json.dumps({"status": "error", "message": "Camera is not connected."})


@app.route('/api/set-config', methods=['POST'])
def set_config():
    global config
    config = request.json("config")
    result = config_handler.set_multiple_configs(config)
    return json.dumps(result)


if __name__ == '__main__':
    app.run(port=5555, host="0.0.0.0")
