import cv2
from flask import Flask, request, json, send_file
import warnings
import os
import pyAesCrypt


#warnings.filterwarnings("ignore")
app = Flask(__name__)


@app.route('/get_photo', methods=['POST', 'GET'])
def result_photo():
    """Returning photo to client."""
    request_data = request.get_json()
    cameraId = request_data['cameraId']

    # We could adjust several cameras by its URLs
    if cameraId == '1':
        camera = 'http://admin:_pass17_@192.168.30.229/ISAPI/Streaming/Channels/101/pictures?snapshotimagetype=JPEG'
    elif cameraId == '2':
        camera = 'rtsp://admin:_pass17_@192.168.30.224:554/ISAPI/Streaming/Channels/101'
    else:
        camera = 'rtsp://admin:_pass17_@192.168.30.229:554/ISAPI/Streaming/Channels/101'

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
        print(str(e))
        s = str(e)
        return s


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=4000)
