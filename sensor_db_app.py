from flask import Flask, Response, Blueprint
from flask import request, jsonify
from flask_restx import Api, Resource, fields
import sys
from pymongo import MongoClient
import decision as dc
from bson.json_util import dumps, loads, default

app = Flask(__name__)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
app.config.SWAGGER_UI_REQUEST_DURATION = True
app.config.RESTX_MASK_SWAGGER = False

#db_statement
client = MongoClient('mongodb://localhost:27017/')
# client = MongoClient('mongodb://mongo-flask-app:27017/')
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

#populate DB
col.delete_many({})
for msrmt in measurements:
  col.insert_one(msrmt).inserted_id

@ns.route('/')
class DeviceWelcomePage(Resource):
    """Shows the welcome page and list of measurements."""
    @ns.doc(description='Shows the welcome page.')
    def get(self):
        """Print Welcome Page and list of measurements."""
        host_address = request.host

        return Response('''<h1>Sensor Measurement Archive</h1>
            <p>A prototype API for IoT device measurements.</p>
            <h3>Host Address: {}</h3>''')
            #<h3>Sensor ID: {}</h3>'''.format(host_address, jsonify(measurements)))

    @ns.doc(description='Shows a list of all measurements service APIs.')
    def get(self):
        """Get all measurements."""
        result = col.find()
        return jsonify(dumps(result, default=default))

## READ IN DATA AND SAVE TO DB
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
        # print(measurement, file=sys.stdout)

        # db_statement
        newElement = col.insert_one(measurement).inserted_id
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
        newElement = col.insert_one(measurement).inserted_id
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
        # print(measurement, file=sys.stdout)

        # # db_statement
        newElement = col.insert_one(measurement).inserted_id
        measurement['id'] = measurements[-1]['id'] + 1
        measurements.append(measurement)
        return measurement, 201

## READ DATA FROM DB AND CONPUTE DECISION
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

        ndvi_result = col.find_one( {
          "i_loc": i_loc,
          "j_loc": j_loc,
          "timestamp": timestamp,
          "type": 'ndvi_sensor'
        } )
        n_result = col.find( {
          "i_loc": { '$in': [ i_loc, i_loc+1] },
          "j_loc": { '$in': [ j_loc, j_loc+1] },
          "timestamp": timestamp,
          "type": "n_sensor"
        } )
        w_result = col.find_one( {
          "timestamp": timestamp,
          "type": "w_sensor"
        })
        N=[]
        K=[]
        P=[]
        for msrmt in n_result:
          N.append(msrmt.get('N'))
          P.append(msrmt.get('P'))
          K.append(msrmt.get('K'))

        result = list(n_result)+list(w_result)+list(ndvi_result)

        if len(result) > 0:
          # Calls the decision making method if entries are found
          dec = dc.fertilizer_decision(N, P, K, ndvi_result.get("NDVI"), w_result.get("wind speed"), timestamp)
          newElement = col.insert_one(loads(dec)).inserted_id
          return dec

        api.abort(404, "Device ID {} doesn't exist".format(id))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)