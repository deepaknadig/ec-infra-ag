import os
import PIL
from PIL import Image
from io import BytesIO

import parsers
from flask import Flask, request, redirect, jsonify, Response, Blueprint
from werkzeug.utils import secure_filename
from flask_restx import Api, Resource, fields, Namespace

from skimage import io
import skimage.data as data
import skimage.segmentation as seg
import skimage.color as color
from pymongo import MongoClient

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# db_statement
#client = MongoClient('mongodb://localhost:27017/')
client = MongoClient('mongodb://mongo-flask-app:27017/')
db = client["testdb"]
col = db["processed_images"]

api = Namespace('image_processing', description='Manage Ag-IoT image processing API services.')


@api.route('/')
class DeviceWelcomePage(Resource):
    """Shows the welcome page and list of measurements."""

    #for testing only
    @api.doc(description='Retrieves the processed images from the DB and saves them locally.')
    def get(self):
        """Get all processed images."""
        result = col.find()
        for item in result:
            image = Image.open(BytesIO(item["file"]))
            #image.save(os.path.join(TEMP_FOLDER, item["filename"]))
        # TODO: find() is not scalable.
        resp = jsonify({'message' : 'Images successfully downloaded'})
        resp.status_code = 201
        return resp


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api.route('/file-upload', methods=['POST'])
class process_image(Resource):
    """Get new image and process it."""

    @api.doc(description='Process the received image and store it in the DB')
    @api.expect(parsers.file_upload)
    def post(self):
        files = parsers.file_upload.parse_args()
        if 'file' not in files:
            resp = jsonify({'message' : 'No file part in the request'})
            resp.status_code = 400
            return resp
        file = files['file']
        if file.filename == '':
            resp = jsonify({'message' : 'No file selected for uploading'})
            resp.status_code = 400
            return resp
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            process_img(filename)
            resp = jsonify({'message' : 'File successfully uploaded'})
            resp.status_code = 201
            return resp
        else:
            resp = jsonify({'message' : 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
            resp.status_code = 400
            return resp

def process_img(filename):
    ## Felzenszwalb
    image = io.imread(os.path.join(UPLOAD_FOLDER, filename))
    image_felzenszwalb = seg.felzenszwalb(image)
    image_felzenszwalb_colored = color.label2rgb(image_felzenszwalb, image, kind='avg')
    f = BytesIO()
    new_img= PIL.Image.fromarray(image_felzenszwalb_colored)
    new_img.save(f, format=filename.split('.')[1])
    encoded = f.getvalue()
    col.insert({"filename": 'felzenszwalb_'+filename, "file": encoded, "description": "felzenszwalb segmentation" })
    
    ## SLIC( Simple Linear Iterative Clustering)
    image_slic = seg.slic(image,n_segments=155)
    image_slic_final = color.label2rgb(image_slic, image, kind='avg')
    f = BytesIO()
    new_img= PIL.Image.fromarray(image_slic_final)
    new_img.save(f, format=filename.split('.')[1])
    encoded = f.getvalue()
    col.insert({"filename": 'SLIC_'+filename, "file": encoded, "description": "SLIC segmentation" })
    