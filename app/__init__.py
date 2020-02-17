from flask import Flask, Blueprint
from flask_restx import Api

from .device import api as device_api
from .measurement import api as measurement_api

app = Flask(__name__)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
app.config.SWAGGER_UI_REQUEST_DURATION = True
app.config.RESTX_MASK_SWAGGER = False

blueprint = Blueprint('api', __name__, url_prefix='/api/v1')

api = Api(blueprint,
          version="1.0",
          title="Ag-IoT Services API",
          description="Manage API services for various Ag-IoT devices.",
          doc='/doc/',
          contact="Deepak Nadig",
          default_mediatype='application/json')

app.register_blueprint(blueprint)

api.add_namespace(device_api)
api.add_namespace(measurement_api)

