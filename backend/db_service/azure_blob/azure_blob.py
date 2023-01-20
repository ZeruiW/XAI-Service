import os
import json
from flask import (
    request, jsonify
)
from xai_backend_central_dev.flask_manager import ExecutorBluePrint
from . import azure_blob_helper

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
        sample_data_set = request.args.get('sample_data_set')
        sample_group = request.args.get('sample_group')

        return jsonify(az.list_blobs(sample_data_set, sample_group))

    if request.method == 'POST':
        files = request.files
        samples = files.getlist('samples')
        sample_data_set = request.form.get('sample_data_set')
        sample_group = request.form.get('sample_group')
        sample_metadata = files.get('sample_metadata')

        sample_save_tmp_path = os.path.join(
            os.environ['COMPONENT_TMP_DIR'], sample_data_set, sample_group)

        if not os.path.exists(sample_save_tmp_path):
            os.makedirs(sample_save_tmp_path, exist_ok=True)

        # read sample metadata
        read_sample_metadata = {}
        if sample_metadata != None and sample_metadata.content_type == 'application/json':
            read_sample_metadata = json.load(sample_metadata)

        # upload sample to blob
        for i in tqdm(range(len(samples))):
            sample = samples[i]
            sample_save_path = os.path.join(
                sample_save_tmp_path, sample.filename)
            sample.save(sample_save_path)

            blob_file_name = os.path.join(
                sample_data_set, sample_group, sample.filename)

            az.upload_blob(blob_file_name, sample_save_path,
                           read_sample_metadata.get(sample.filename))

    return ""
