from flask import Flask, Response, Blueprint
from flask import request, jsonify
from flask_restx import Api, Resource, fields
import sys

app = Flask(__name__)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
app.config.SWAGGER_UI_REQUEST_DURATION = True
app.config.RESTX_MASK_SWAGGER = False

api_v1 = Blueprint('api', __name__, url_prefix='/api/v1')

api = Api(api_v1,
          version="1.0",
          title="Ag-IoT Services API",
          description="Manage API services for various Ag-IoT devices.",
          doc='/doc/',
          contact="Deepak Nadig",
          default_mediatype='application/json')

app.register_blueprint(api_v1)

ns = api.namespace('devices', description='Manage Ag-IoT device API services.')

device_model = api.model('Device Data Model', {
    'id': fields.Integer(readonly=True, description='The unique identifier for the measurement'),
    'device-id': fields.String(required=True, description='The measurement device ID'),
    'timestamp': fields.Float(required=True, description='The measurement timestamp'),
    'temperature': fields.Float(required=True, description='The measured temperature'),
    'unit': fields.String(required=True, description='The temperature unit'),
})

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


@ns.route('/')
class DeviceWelcomePage(Resource):
    """Shows the welcome page."""

    @ns.doc(description='Shows the welcome page.')
    def get(self):
        """Print Welcome Page."""
        host_address = request.host
        return Response('''<h1>Sensor Measurement Archive</h1>
            <p>A prototype API for IoT device measurements.</p>
            <h3>Host Address: {}</h3>'''.format(host_address))


@ns.route('/device')
class DeviceMeasurements(Resource):
    """Shows a list of all device measurement service APIs."""

    @ns.doc(description='Shows a list of all device measurement service APIs.')
    def get(self):
        """Get all measurements."""
        return jsonify(devices)

    @ns.doc(description='Add new device measurements.')
    @ns.expect(device_model)
    @ns.marshal_with(device_model, code=201)
    def post(self):
        """Add device measurements"""
        device = api.payload
        device['id'] = devices[-1]['id'] + 1
        print(device, file=sys.stdout)
        devices.append(device)
        return device, 201


@ns.route('/<int:id>')
@ns.response(404, 'Device ID not found.')
@ns.param('id', 'The Device ID')
class DeviceById(Resource):
    @ns.doc(description='Show device measurements by ID.',
            params={'id': 'Specify the Device ID'})
    @ns.marshal_with(device_model, mask='device-id, timestamp, temperature, unit')
    def get(self, id):
        """Show device measurements by ID"""
        for device in devices:
            if device['id'] == id:
                return device
        api.abort(404, "Device ID {} doesn't exist".format(id))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
