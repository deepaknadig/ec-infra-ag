import sys

from flask import Response
from flask import request
from flask_restx import Resource, fields, Namespace
from bson.json_util import dumps
from models import mongo_client
from tasks import celery
import config
import time

api = Namespace('device', description='Ag-IoT Device operations APIs.')

device_model = api.model('Device Data Model', {
    'device_id': fields.String(required=True, description='The measurement device ID'),
    'timestamp': fields.Float(required=True, description='The measurement timestamp'),
})

# DB
db = mongo_client[config.MONGO_DATABASE]
col = db["device"]

col.delete_many({})

# Populate devicedb with dummy data
devices = [
    {'device_id': 'sens01',
     'timestamp': '1581107171.770178'},
    {'device_id': 'sens02',
     'timestamp': '1581107389.182897'},
    {'device_id': 'sens03',
     'timestamp': '1581107419.304042'}
]
for device in devices:
    if not col.find_one(device):
        col.insert_one(device)


@api.route('/')
class DeviceRoot(Resource):
    """The device API root."""

    @api.doc(description='Shows the welcome page.')
    def get(self):
        """Print Welcome Page."""
        host_address = request.host
        result = device_add.delay(1900, 47)
        return Response('''<h1>Device API</h1>
            <p>IoT device operations API.</p>
            <h4>Host Address: {}</h4>
            <h4>Host Address: {}</h4>'''.format(host_address, result))


@api.route('/devices')
class DeviceList(Resource):
    """APIs for working with all devices."""

    @api.doc(description='List all devices.')
    def get(self):
        """Get all devices."""
        result = col.find()
        return Response(response=dumps(result), status=201, mimetype="application/json")

    @api.doc(description='Add a new device.')
    @api.expect(device_model)
    @api.marshal_with(device_model, code=201)
    def post(self):
        """Add devices"""
        data = api.payload
        s = col.find_one({'device_id': request.json['device_id']})
        if s:
            api.abort(500, "Device with ID {} exists".format(request.json['device_id']))
        else:
            col.insert_one(data)
        return data, 201


@api.route('/<device_id>')
@api.param('device_id', 'The Device ID')
@api.response(404, 'Device ID not found.')
class DeviceById(Resource):
    @api.doc(description='Show device measurements by ID.')
    @api.marshal_with(device_model)
    def get(self, device_id):
        """Show device by ID"""
        s = col.find_one({'device_id': device_id})
        print(s, file=sys.stderr)
        if s:
            return s, 200
        api.abort(404, "Device ID {} doesn't exist".format(device_id))


@celery.task()
def device_add(a, b):
    time.sleep(10)
    return a + b
