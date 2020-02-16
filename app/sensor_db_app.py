from flask import Flask, Response, Blueprint
from flask import request, jsonify
from flask_restx import Api, Resource, fields
from pymongo import MongoClient
import decision as dc
from bson.json_util import dumps, loads, default

app = Flask(__name__)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
app.config.SWAGGER_UI_REQUEST_DURATION = True
app.config.RESTX_MASK_SWAGGER = False

# db_statement
#client = MongoClient('mongodb://mongo-flask-app:27017/')
client = MongoClient('mongodb://localhost:27017/')
db = client["testdb"]
col = db["measurements"]

api_v1 = Blueprint('api', __name__, url_prefix='/api/v1')

api = Api(api_v1,
          version="1.0",
          title="Ag-IoT Services API",
          description="Manage API services for various Ag-IoT devices.",
          doc='/doc/',
          contact="Deepak Nadig",
          default_mediatype='application/json')

app.register_blueprint(api_v1)

ns = api.namespace('measurements', description='Manage Ag-IoT device API services.')

# All models:
#   Nutrients sensors: n_sensor
#   NDVI sensor: ndvi_sensor
#   wind sensor: w_sensor
n_sensor_model = api.model('Nutrient Sensor Data Model', {
    'i_loc': fields.Integer(required=True, description='i coordinate of the grid cell'),
    'j_loc': fields.Integer(required=True, description='j coordinate of the grid cell'),
    'timestamp': fields.Integer(required=True, description='The measurement timestamp'),
    'N': fields.Float(required=True, description='Measured Nitrogen'),
    'P': fields.Float(required=True, description='Measured Phosphate'),
    'K': fields.Float(required=True, description='Measured Potassium'),
    'type': fields.String(readonly=True, description='Sensor Type n_sensor'),
})
ndvi_sensor_model = api.model('NDVI Sensor Data Model', {
    'i_loc': fields.Integer(required=True, description='i coordinate of the grid cell'),
    'j_loc': fields.Integer(required=True, description='j coordinate of the grid cell'),
    'timestamp': fields.Integer(required=True, description='The measurement timestamp'),
    'NDVI': fields.Float(required=True, description='Measured NDVI'),
    'type': fields.String(readonly=True, description='Sensor Type ndvi_sensor'),
})
w_sensor_model = api.model('Wind Speed Sensor Data Model', {
    'timestamp': fields.Integer(required=True, description='The measurement timestamp'),
    'wind speed': fields.Float(required=True, description='Measured wind speed'),
    'type': fields.String(readonly=True, description='Sensor Type w_sensor'),
})

measurements = [
    {'id': 0,
     'i_loc': 0,
     'j_loc': 0,
     'timestamp': 1,
     'N': 45,
     'P': 2,
     'K': 190,
     'type': 'n_sensor'},
    {'id': 1,
     'i_loc': 0,
     'j_loc': 0,
     'timestamp': 1,
     'NDVI': 0.5,
     'type': 'ndvi_sensor'},
    {'id': 2,
     'timestamp': 1,
     'wind speed': 3,
     'type': 'w_sensor'},
    {'K': 120,
     'N': 45,
     'P': 3,
     'i_loc': 0,
     'id': 3,
     'j_loc': 1,
     'timestamp': 1,
     'type': 'n_sensor'},
    {'K': 125,
     'N': 50,
     'P': 4,
     'i_loc': 1,
     'id': 4,
     'j_loc': 1,
     'timestamp': 1,
     'type': 'n_sensor'},
    {'K': 115,
     'N': 49,
     'P': 3.5,
     'i_loc': 1,
     'id': 5,
     'j_loc': 0,
     'timestamp': 1,
     'type': 'n_sensor'}
]

# populate DB
#col.delete_many({})
for msrmt in measurements:
    col.insert_one(msrmt)


@ns.route('/')
class DeviceWelcomePage(Resource):
    """Shows the welcome page and list of measurements."""

    @ns.doc(description='Shows a list of all measurements service APIs.')
    def get(self):
        """Get all measurements."""
        result = col.find()
        # TODO: find() is not scalable.
        return Response(response=dumps(result), status=201, mimetype="application/json")


# READ IN DATA AND SAVE TO DB
@ns.route('/nutrients')
class ReceiveNutrientMeasurements(Resource):
    """Get new nutrients measurement service APIs."""

    @ns.doc(description='Add new nutrients measurement.')
    @ns.expect(n_sensor_model)
    @ns.marshal_with(n_sensor_model, code=201)
    def post(self):
        """Add measurement"""
        measurement = api.payload
        measurement['type'] = "n_sensor"

        # db_statement
        col.insert_one(measurement)
        measurement['id'] = measurements[-1]['id'] + 1
        measurements.append(measurement)
        return measurement, 201


@ns.route('/ndvi')
class ReceiveNDVIMeasurements(Resource):
    """Get new NDVI measurement service APIs."""

    @ns.doc(description='Add new NDVI measurement.')
    @ns.expect(ndvi_sensor_model)
    @ns.marshal_with(ndvi_sensor_model, code=201)
    def post(self):
        """Add measurement"""
        measurement = api.payload
        measurement['type'] = "ndvi_sensor"
        # print(measurement, file=sys.stdout)

        # # db_statement
        col.insert_one(measurement)
        measurement['id'] = measurements[-1]['id'] + 1
        measurements.append(measurement)
        return measurement, 201


@ns.route('/wind')
class ReceiveWindMeasurements(Resource):
    """Get new wind speed measurement service APIs."""

    @ns.doc(description='Add new wind speed measurement.')
    @ns.expect(w_sensor_model)
    @ns.marshal_with(w_sensor_model, code=201)
    def post(self):
        """Add measurement"""
        measurement = api.payload
        measurement['type'] = "w_sensor"

        # db_statement
        col.insert_one(measurement)
        measurement['id'] = measurements[-1]['id'] + 1
        measurements.append(measurement)
        return measurement, 201


# READ DATA FROM DB AND CONPUTE DECISION
@ns.route('/<int:i_loc>/<int:j_loc>/<int:timestamp>')
@ns.response(404, 'No measurements for location and time specified.')
@ns.param('i_loc', 'i coordinate of the grid cell')
@ns.param('j_loc', 'j coordinate of the grid cell')
@ns.param('timestamp', 'timestamp of measurement')
class DecisionByLocation(Resource):
    @ns.doc(description='Show fertilizer decision by location.',
            params={'i_loc': 'i coordinate of the grid cell',
                    'j_loc': 'j coordinate of the grid cell',
                    'timestamp': 'timestamp of the measurement'})
    def get(self, i_loc, j_loc, timestamp):
        """Show measurement for a specific location at a certain time"""
        N = []
        K = []
        P = []
        ndvi_result = col.find_one({
            "i_loc": i_loc,
            "j_loc": j_loc,
            "timestamp": timestamp,
            "type": 'ndvi_sensor'
        })
        for i in range(i_loc, i_loc+2):
            for j in range (j_loc, j_loc+2):
                n_result = col.find_one({
                    "i_loc": {'$in': [i_loc]},
                    "j_loc": {'$in': [j_loc]},
                    "timestamp": timestamp,
                    "type": "n_sensor"
                })
                N.append(n_result.get('N'))
                P.append(n_result.get('P'))
                K.append(n_result.get('K'))

        w_result = col.find_one({
            "timestamp": timestamp,
            "type": "w_sensor"
        })

        result = N + list(w_result) + list(ndvi_result)

        if len(result) > 0:
            # Calls the decision making method if entries are found
            dec = dc.fertilizer_decision(N, P, K, ndvi_result.get("NDVI"), w_result.get("wind speed"), timestamp)
            col.insert_one(loads(dec))
            return Response(response=dec, status=200, mimetype="application/json")

        api.abort(404, "Device ID {} doesn't exist".format(id))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
