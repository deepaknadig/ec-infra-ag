from io import BytesIO

import PIL
import numpy as np

import config
from api import parsers
import skimage.color as color
import skimage.segmentation as seg
from PIL import Image
from flask import jsonify
from flask_restx import Resource, Namespace
from models import mongo_client
from werkzeug.utils import secure_filename
import json
from tasks import celery
import os

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# db_statement
db = mongo_client[config.MONGO_DATABASE]
col = db["processed_images"]

api = Namespace('compute', description='Manage Ag-IoT image processing API services.')


@api.route('/')
class DeviceWelcomePage(Resource):
    """Shows the welcome page and list of measurements."""

    # for testing only
    @api.doc(description='Retrieves the processed images from the DB and saves them locally.')
    def get(self):
        """Get all processed images."""
        result = col.find()
        for item in result:
            image = Image.open(BytesIO(item["file"]))
            image.save(os.path.join(config.WORKER_STORE, item["filename"]))
        # TODO: find() is not scalable.
        resp = jsonify({'message': 'Images successfully downloaded'})
        resp.status_code = 201
        return resp


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@api.route('/image/segmentation/felzenszwalb', methods=['POST'])
class FelzenszwalbSegmentation(Resource):
    """Perform Felzenszwalb Image Segmentation."""

    @api.doc(description='Process the received image and store it in the DB')
    @api.expect(parsers.file_upload)
    def post(self):
        files = parsers.file_upload.parse_args()
        if 'file' not in files:
            resp = jsonify({'message': 'No file part in the request'})
            resp.status_code = 400
            return resp
        file = files['file']
        if file.filename == '':
            resp = jsonify({'message': 'No file selected for uploading'})
            resp.status_code = 400
            return resp
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.seek(0)

            image = np.array(Image.open(file))
            # alternative
            # nparr = np.fromfile(file, np.uint8)
            # image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Numpy ndarray to json conversion
            image_json = json.dumps({'image': image}, cls=NumpyEncoder)

            felzenszwalb_segmentation.delay(image_json, filename)
            resp = jsonify({'message': 'Image  uploaded successfully. Image queued for segmentation.'})
            resp.status_code = 201
            return resp
        else:
            resp = jsonify({'message': 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
            resp.status_code = 400
            return resp


@api.route('/image/segmentation/slic', methods=['POST'])
class SlicSegmentation(Resource):
    """Perform SLIC Image Segmentation."""

    @api.doc(description='Process the received image and store it in the DB')
    @api.expect(parsers.file_upload)
    def post(self):
        files = parsers.file_upload.parse_args()
        if 'file' not in files:
            resp = jsonify({'message': 'No file part in the request'})
            resp.status_code = 400
            return resp
        file = files['file']
        if file.filename == '':
            resp = jsonify({'message': 'No file selected for uploading'})
            resp.status_code = 400
            return resp
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.seek(0)

            image = np.array(Image.open(file))

            # Numpy ndarray to json conversion
            json_dump_image = json.dumps({'image': image}, cls=NumpyEncoder)

            slic_segmentation.delay(json_dump_image, filename)
            resp = jsonify({'message': 'Image  uploaded successfully. Image queued for segmentation.'})
            resp.status_code = 201
            return resp
        else:
            resp = jsonify({'message': 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
            resp.status_code = 400
            return resp


@celery.task(acks_late=True)
def felzenszwalb_segmentation(json_image, filename):
    # Preprocess json dump to image
    json_load = json.loads(json_image)
    image = np.asarray(json_load["image"]).astype(np.uint8)

    # 1- Felzenszwalb
    image_felzenszwalb = seg.felzenszwalb(image)
    image_felzenszwalb_colored = color.label2rgb(image_felzenszwalb, image, kind='avg')
    f = BytesIO()
    new_img = PIL.Image.fromarray(image_felzenszwalb_colored)
    new_img.save(f, format=filename.split('.')[1])
    encoded = f.getvalue()
    # TODO: Use the configured CELERY_RESULT_BACKEND to store the image.
    col.insert({"filename": 'felzenszwalb_' + filename, "file": encoded, "description": "felzenszwalb segmentation"})


@celery.task(acks_late=True)
def slic_segmentation(json_image, filename):
    # Preprocess json dump to image
    json_load = json.loads(json_image)
    image = np.asarray(json_load["image"]).astype(np.uint8)

    # 2- SLIC( Simple Linear Iterative Clustering)
    image_slic = seg.slic(image, n_segments=155)
    image_slic_final = color.label2rgb(image_slic, image, kind='avg')
    f = BytesIO()
    new_img = PIL.Image.fromarray(image_slic_final)
    new_img.save(f, format=filename.split('.')[1])
    encoded = f.getvalue()
    # TODO: Use the configured CELERY_RESULT_BACKEND to store the image.
    col.insert({"filename": 'SLIC_' + filename, "file": encoded, "description": "SLIC segmentation"})


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
