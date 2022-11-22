from base64 import encodebytes
import io
import json
import mysql.connector
from flask import (
    Blueprint, request, jsonify
)
from PIL import Image
import numpy as np

bp = Blueprint('imgnet1000', __name__, url_prefix='/db/imgnet1000')

cnx = mysql.connector.connect(
    host="database-1.c0gj2xdlz1ck.us-east-2.rds.amazonaws.com",
    user="xai",
    password="xaidb.2022",
    database="xaifw"
)


def insert_img(img_name, img_data, img_group):
    cursor = cnx.cursor()
    add_img = (
        "INSERT INTO image_net_1000(img_name, img_data, img_group) VALUES (%s,%s,%s)")
    data = (img_name, img_data, img_group)
    cursor.execute(add_img, data)
    cnx.commit()
    cursor.close()


@bp.route('/', methods=['POST'])
def upload_paper():
    if request.method == 'POST':
        files = request.files
        imgs = files.getlist('imgs')

        for img in imgs:
            img_name = img.filename
            img_data = img.read()
            # img = np.array(Image.open(img))

            insert_img(img_name, img_data, 'test')

    return ""


def get_response_image(img_data):
    pil_img = Image.open(io.BytesIO(img_data))  # reads the PIL image
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG')  # convert the PIL image to byte array
    encoded_img = encodebytes(byte_arr.getvalue()).decode(
        'ascii')  # encode as base64
    return encoded_img


@bp.route('/', methods=['GET'])
def list_img():
    l = []
    scope = request.args['scope']
    with_img_data = request.args['with_img_data'] == '1'
    if request.method == 'GET':
        cursor = cnx.cursor()
        if scope == 'all':
            q = (
                f"SELECT id, img_name, {' img_data,' if with_img_data else ''} img_group FROM image_net_1000")
            cursor.execute(q)
        else:
            img_name_list = request.args['img_name_list']
            # print(img_name_list)
            img_name_list = [f'\'{x}\'' for x in json.loads(img_name_list)]
            qs = ','.join(img_name_list)
            q = (
                f"SELECT id, img_name, {' img_data,' if with_img_data else ''} img_group FROM image_net_1000 WHERE img_name IN({qs})")
            # print(q)
            cursor.execute(q)
        if with_img_data:
            for (id, img_name, img_data, img_group) in cursor:
                l.append((id, img_name, get_response_image(img_data), img_group,))
                # Image.open(io.BytesIO(img_data)).show()
        else:
            for (id, img_name, img_group) in cursor:
                l.append((id, img_name, img_group,))
                # Image.open(io.BytesIO(img_data)).show()

        cnx.commit()
        cursor.close()

    return jsonify(l)
