import flask
from flask import request, jsonify, abort
from flask_restx import Api, Resource

app = flask.Flask(__name__)
app.config["DEBUG"] = True


# Create test data as a list of dictionaries.
devices = [
    {'id': 0,
     'device-id': 'sens01',
     'timestamp': '1581107171.770178',
     'temperature': '37.3',
     'unit': 'Fahrenheit'},
    {'id': 1,
     'device-id': 'sens02',
     'timestamp': '1581107389.182897',
     'temperature': '11.5',
     'unit': 'Celsius'},
    {'id': 2,
     'device-id': 'sens01',
     'timestamp': '1581107419.304042',
     'temperature': '41.9',
     'unit': 'Fahrenheit'}
]


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Sensor Measurement Archive</h1>
<p>A prototype API for IoT device measurements.</p>'''


@app.route('/api/v1/group/devices/all', methods=['GET'])
def api_all():
    return jsonify(devices)


@app.route('/api/v1/group/devices/', methods=['GET'])
def api_id():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specify an id."

    # Create an empty list for our results
    results = []

    # Loop through the data and match results that fit the requested ID.
    for device in devices:
        if device['id'] == id:
            results.append(device)

    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.
    return jsonify(results)


@app.route('/api/v1/group/devices/add', methods=['POST'])
def create_device_entry():
    if not request.json or not 'device-id' in request.json:
        abort(400)
    device = {
        'id': devices[-1]['id'] + 1,
        'device-id': request.json['device-id'],
        'timestamp': request.json.get('timestamp', ""),
        'temperature': request.json.get('temperature', ""),
        'unit': request.json.get('unit', "")
    }
    devices.append(device)
    return jsonify({'device': device}), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0')
