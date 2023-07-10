from flask import Flask, request, json
import warnings
from ultralytics import YOLO
from ultralytics.yolo.v8.detect.predict import DetectionPredictor
import json
from base64 import b64decode
import cv2
from numpy import frombuffer
from shapely.geometry import Point, Polygon

model = YOLO('yolov8n.pt')
warnings.filterwarnings("ignore")
app = Flask(__name__)


def countPeople():
    """Count the people in Frame understanding that we may have the mirrors."""
    results = model.predict(source='runs/photo_4.jpg', show=True, imgsz=1920, save=True, conf=0.2, line_thickness=1,
                            classes=[0])  # predict on an image

    return counter


def inPolygon(x, y, xp, yp):
    """Checking if coordinate in polygon or not."""
    c = 0
    for i in range(len(xp)):
        if (((yp[i] <= y and y < yp[i - 1]) or (yp[i - 1] <= y and y < yp[i])) and
                (x > (xp[i - 1] - xp[i]) * (y - yp[i]) / (yp[i - 1] - yp[i]) + xp[i])): c = 1 - c
    return c


def checkIfInside(border, target):
    # Create Point objects
    p = Point(target[0], target[1])
    poly = Polygon(border)
    return poly.contains(p)


@app.route('/count', methods=['GET', 'POST'])
def result():
    """Returning counter to client."""
    counter = 0
    data = json.loads(request.stream.read())
    Id = data.get('Id', None)
    coords = data.get('params', None)

    image = b64decode(data.get('img', None))
    with open(r'image.jpg', 'wb') as x:
        x.write(image)
    image_cv2 = cv2.imread('image.jpg')

    npImg = frombuffer(image)
    decImg = cv2.imdecode(npImg, 1)
    decImg_w = decImg.shape[1]
    decImg_h = decImg.shape[0]

    polygon_x = []
    polygon_y = []
    border = []
    for coord in coords['coordinates']:
        border.append((round(coord[0] * decImg_w / 100), round(coord[1] * decImg_h / 100)))
        print(coord[0], coord[1])
        polygon_x.append(coord[0])
        polygon_y.append(coord[1])
        cv2.circle(image_cv2, (round(coord[0] * decImg_w / 100), round(coord[1] * decImg_h / 100)), 10, (100, 200, 10), -1)

    print(coords['coordinates'])

    results = model.predict(source='image.jpg', show=True, imgsz=1920, save=True, conf=0.25, line_thickness=1,
                            classes=[0])

    # Check our person in polygon it or not
    counter = 0
    boxes = results[0].boxes
    border.append(border[0])
    print(border)
    for box in boxes:  # returns one box
        if checkIfInside(border, (box.xyxy[0][0].item(), box.xyxy[0][3].item())) and \
            checkIfInside(border, (box.xyxy[0][2].item(), box.xyxy[0][3].item())):
            print('1')
            counter += 1
        else:
            print('0')

    print(counter)


    response = app.response_class(
        response=json.dumps(counter),
        status=200,
        mimetype='application/json'
    )

    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)
