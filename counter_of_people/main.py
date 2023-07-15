from flask import Flask, request, json
import warnings
from ultralytics import YOLO
from ultralytics.yolo.v8.detect.predict import DetectionPredictor
import json
from base64 import b64decode
import cv2
from numpy import frombuffer
from shapely.geometry import Point, Polygon
from threading import Thread
import os
from time import time
import psycopg2
import pandas as pd


model = YOLO('yolov8n.pt')
warnings.filterwarnings("ignore")
app = Flask(__name__)
app.config['TIME'] = time()
app.config['COUNTER'] = []


def count_time():
    '''Counting time for lounching the recognition.'''
    hours = 0
    minutes = 0
    seconds = 1
    limit = seconds + minutes * 60 + hours * 60 * 60
    while True:
        if time() - app.config['TIME'] > limit:
            app.config['TIME'] = time()
            check_images()
            return


def check_images():
    """Taking the image from queue and recognition it."""
    if len(os.listdir('queue')) != 0:
        image_cv2 = cv2.imread('queue\\' + os.listdir('queue')[0])
        file_id = os.listdir('queue')[0].split('.')[0]

        decImg_h, decImg_w = image_cv2.shape[:2]
        polygon_x, polygon_y, border = [], [], []

        connection_stadium = psycopg2.connect(dbname='stadium', user='postgres',
                                                     password='qwerty', host='localhost', port="5432")

        # Loading the datas from DataBase
        data = pd.read_sql_query("SELECT * FROM recognition WHERE order_id=" + file_id,
                                 con=connection_stadium)
        coords = []
        new_coord = []
        step = 0
        for coord in data.iloc[0]['coords'].split(','):
            if coord:
                step += 1
                if step == 1:
                    new_coord.append(float(coord))
                if step == 2:
                    step = 0
                    new_coord.append(float(coord))
                    coords.append(new_coord)
                    new_coord = []

        for coord in coords:
            border.append((round(coord[0] * decImg_w / 100), round(coord[1] * decImg_h / 100)))
            polygon_x.append(coord[0])
            polygon_y.append(coord[1])
            cv2.circle(image_cv2, (round(coord[0] * decImg_w / 100), round(coord[1] * decImg_h / 100)),
                       10, (100, 200, 10), -1)

        results = model.predict(source='queue\\' + os.listdir('queue')[0], imgsz=1920, conf=0.25, classes=[0])

        counter = 0
        # Check our person in polygon it or not
        boxes = results[0].boxes
        border.append(border[0])
        for box in boxes:
            if checkIfInside(border, (box.xyxy[0][0].item(), box.xyxy[0][3].item())) and \
                    checkIfInside(border, (box.xyxy[0][2].item(), box.xyxy[0][3].item())):
                counter += 1

        cursor = connection_stadium.cursor()
        # Storing the datas to DataBase
        cursor.execute("UPDATE recognition SET counter={}, status=1 WHERE order_id={}".format(counter, file_id))
        connection_stadium.commit()
        os.remove('queue\\' + os.listdir('queue')[0])
    else:
        return -1


def checkIfInside(border, target):
    """Checking if point in polygon or not."""
    return Polygon(border).contains(Point(target[0], target[1]))


@app.route('/recognition', methods=['GET', 'POST'])
def store():
    """Saving datas for recognition."""
    data = json.loads(request.stream.read())
    id = data.get('id', None)
    camid = data.get('camid', None)
    sectorid = data.get('sectorid', None)
    type = data.get('type', None)
    coords = data.get('params', None)

    camera_image = b64decode(data.get('img', None))
    with open(r'queue\\{}.jpg'.format(id), 'wb') as image:
        image.write(camera_image)

    crd = ''
    for coord in coords['coordinates']:
        crd = crd + str(coord[0]) + ',' + str(coord[1]) + ','

    connection_stadium = psycopg2.connect(dbname='stadium', user='postgres',
                                                 password='qwerty', host='localhost', port="5432")
    cursor = connection_stadium.cursor()
    # Storing the datas to DataBase
    cursor.execute("INSERT INTO recognition(order_id, cam_id, sector_id, \
    type, coords, status) \
    VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(id, camid, sectorid, type, crd, 0))
    connection_stadium.commit()
    connection_stadium.close()

    response = app.response_class(
        response=json.dumps({'status': 1}),
        status=200,
        mimetype='application/json'
    )

    return response


@app.route('/counter', methods=['GET', 'POST'])
def result():
    """Returning the counter."""
    data = json.loads(request.stream.read())
    id = data.get('id', None)

    connection_stadium = psycopg2.connect(dbname='stadium', user='postgres',
                                          password='qwerty', host='localhost', port="5432")

    # Loading the datas from DataBase
    data = pd.read_sql_query("SELECT * FROM recognition WHERE order_id={}".format(id), con=connection_stadium)
    if len(data) != 1:
        res = -1
    else:
        res = int(data.iloc[0]['counter'])
    connection_stadium.close()

    response = app.response_class(
        response=json.dumps({'counter': res}),
        status=200,
        mimetype='application/json'
    )

    return response


if __name__ == "__main__":
    if not os.path.isdir('queue'):
        os.mkdir('queue')

    thread_timer = Thread(target=count_time)
    thread_timer.start()
    app.run(host='0.0.0.0', debug=False)
