import os
import json
from flask import (
    request, jsonify
)
from xai_backend_central_dev.flask_manager import ExecutorBluePrint
from xai_backend_central_dev import azure_blob_helper

from tqdm import tqdm

bp = ExecutorBluePrint(
    'azure_blob', __name__, component_path=__file__, url_prefix='/azure_blob', mongo=False)

az = azure_blob_helper.AZ()


@bp.route('/data_zip', methods=['GET', 'POST'])
def blob_data():
    if request.method == 'GET':
        pass


@bp.route('/', methods=['GET', 'POST'])
def blob():
    if request.method == 'GET':
        data_set_name = request.args.get('data_set_name')
        data_set_group_name = request.args.get('data_set_group_name')
        with_content = request.args.get('with_content')

        return jsonify(az.get_blobs(data_set_name, data_set_group_name, with_content != None))

    if request.method == 'POST':
        files = request.files
        samples = files.getlist('samples')
        data_set_name = request.form.get('data_set_name')
        data_set_group_name = request.form.get('data_set_group_name')
        sample_metadata = files.get('sample_metadata')

        # read sample metadata
        read_sample_metadata = {}
        if sample_metadata != None and sample_metadata.content_type == 'application/json':
            read_sample_metadata = json.load(sample_metadata)

        # upload sample to blob
        for i in tqdm(range(len(samples))):
            sample = samples[i]

            blob_file_name = os.path.join(
                data_set_name, data_set_group_name, sample.filename)

            az.upload_blob(sample.stream, blob_file_name,
                           read_sample_metadata.get(sample.filename))

    return ""
