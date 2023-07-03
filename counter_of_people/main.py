from flask import Flask, request, json
import warnings
from ultralytics import YOLO
from ultralytics.yolo.v8.detect.predict import DetectionPredictor

warnings.filterwarnings("ignore")
app = Flask(__name__)


@app.route('/count', methods=['POST'])
def result():
    """Returning counter to client."""
    counter = 0
    data = json.loads(request.stream.read())
    Id = data.get('Id', None)
    coords = data.get('coords', None)
    counter = coords[4]

    response = app.response_class(
        response=json.dumps(counter),
        status=200,
        mimetype='application/json'
    )

    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)
