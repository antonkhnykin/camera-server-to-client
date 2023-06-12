import cv2
from flask import Flask, request, json, send_file
import warnings
import os
import pyAesCrypt


warnings.filterwarnings("ignore")
app = Flask(__name__)


@app.route('/get_photo', methods=['POST', 'GET'])
def result_photo():
    """Returning photo to client."""
    request_data = request.get_json()
    cameraId = request_data['cameraId']

    # We could adjust several cameras by its URLs
    if cameraId == '1':
        camera = 0
    elif cameraId == '2':
        camera = 0
    else:
        camera = 0

    try:
        cap = cv2.VideoCapture(camera)
        ret, frame = cap.read()
        print("camera =", cameraId)

        cwd = os.getcwd()
        while cap.isOpened():
            if not os.path.isdir(cwd + '/camera'):
                os.mkdir(cwd + '/camera')
            cv2.imwrite(cwd + '/camera/photo.jpg', frame)
            pyAesCrypt.encryptFile(cwd + '/camera/photo.jpg', cwd + '/camera/photo._pg', 'qwerty', 64 * 1024)
            cap.release()
            return send_file(cwd + '/camera/photo._pg', download_name='photo._pg', as_attachment=True)
    except Exception as e:
        s = str(e)
        return s


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, port=4000)
