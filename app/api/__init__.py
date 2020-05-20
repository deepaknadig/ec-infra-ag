import time
from flask import jsonify, Blueprint
from flask_restx import Api, Resource
from tasks import celery
from celery import current_app
import config
from prometheus_flask_exporter import PrometheusMetrics

from .device import api as device_api
from .measurement import api as measurement_api
from .compute import api as compute_api

blueprint = Blueprint('api', __name__, url_prefix=config.API_PREFIX)

api = Api(blueprint,
          version="1.0",
          title="Ag-IoT Services API",
          description="Manage API services for various Ag-IoT devices.",
          doc='/doc/',
          contact="Deepak Nadig",
          default_mediatype='application/json')

# api = Api(prefix=config.settings.BaseConfig.API_PREFIX)

metrics = PrometheusMetrics(app=None, defaults_prefix='ergo')

api.add_namespace(device_api)
api.add_namespace(measurement_api)
api.add_namespace(compute_api)

task_list = list()


class TaskStatusAPI(Resource):
    def get(self):
        return {'task_list': task_list}
    # def get(self, task_id):
    #     task = celery.AsyncResult(task_id)
    #     return jsonify(task.result)


class DataProcessingAPI(Resource):
    def post(self):
        task = process_data.delay()
        task_list.append([task.id, task.status])
        return {'task_id': task.id, 'task_list': task_list}, 200


@celery.task()
def process_data():
    time.sleep(60)
    return 999


# data processing endpoint
api.add_resource(DataProcessingAPI, '/process_data')

# task status endpoint
# api.add_resource(TaskStatusAPI, '/tasks/<string:task_id>')
api.add_resource(TaskStatusAPI, '/tasks')
