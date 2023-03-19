from base64 import encodebytes
import io
import os
import flask
from flask import (
    Blueprint, request, jsonify
)
from PIL import Image
from . import db_helper
from xai_backend_central_dev.flask_manager import ExecutorBluePrint

bp = ExecutorBluePrint(
    'image_net_1000', __name__, component_path=__file__, url_prefix='/db/imgnet1000')


def insert_img_db_exe(cnx, img_name, img_data, img_group, img_label):
    cursor = cnx.cursor()
    add_img = (
        "INSERT INTO image_net_1000(img_name, img_data, img_group, img_label) VALUES (%s,%s,%s,%s)")
    data = (img_name, img_data, img_group, img_label)
    cursor.execute(add_img, data)
    cnx.commit()
    cursor.close()


@bp.route('/', methods=['POST'])
def insert_img_req():
    if request.method == 'POST':
        files = request.files
        imgs = files.getlist('imgs')
        img_label_map = files.get('img_label_map')

        line = img_label_map.readlines()
        m = {}
        for l in line:
            l = l.decode("utf-8").strip().split(',')
            m[l[1]] = l[-1]

        img_group = request.form.get('img_group')
        i = 0
        for img in imgs:
            print(i)
            img_name = img.filename
            img_data = img.read()
            # img = np.array(Image.open(img))
            # insert_img_db_exe(img_name, img_data, img_group, m[img_name])
            db_helper.trans(insert_img_db_exe, img_name,
                            img_data, img_group, m[img_name])
            i += 1

    return ""


def get_response_image(img_data):
    pil_img = Image.open(io.BytesIO(img_data)).convert(
        'RGB')  # reads the PIL image
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG')  # convert the PIL image to byte array
    encoded_img = encodebytes(byte_arr.getvalue()).decode(
        'ascii')  # encode as base64
    return encoded_img


def get_img_db_exe(cnx, img_group, with_img_data):
    l = []
    cursor = cnx.cursor()
    q = (
        f"SELECT id, img_name, {' img_data,' if with_img_data else ''} img_group, img_label FROM image_net_1000 WHERE img_group = '{img_group}'")
    # print(q)
    cursor.execute(q)
    if with_img_data:
        for (id, img_name, img_data, img_group, img_label) in cursor:
            l.append((id, img_name, get_response_image(
                img_data), img_group, img_label))
            # Image.open(io.BytesIO(img_data)).show()
    else:
        for (id, img_name, img_group, img_label) in cursor:
            l.append((id, img_name, img_group, img_label))
            # Image.open(io.BytesIO(img_data)).show()

    cursor.close()
    return l


@bp.route('/', methods=['GET'])
def list_img():

    img_group = request.args.get('img_group')
    if img_group == None:
        return "plese provide img_group"
    with_img_data = request.args.get('with_img_data') != None
    if request.method == 'GET':
        l = db_helper.trans(get_img_db_exe, img_group, with_img_data)

    return jsonify(l)
