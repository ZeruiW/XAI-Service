from base64 import encodebytes
import io
import json
import mysql.connector
from flask import (
    Blueprint, request, jsonify
)
from PIL import Image
import numpy as np

bp = Blueprint('arxiv_cs', __name__, url_prefix='/db/arxiv_cs')

cnx = mysql.connector.connect(
    host="database-1.c0gj2xdlz1ck.us-east-2.rds.amazonaws.com",
    user="xai",
    password="xaidb.2022",
    database="xaifw"
)


@bp.route('/', methods=['POST'])
def upload_paper():
    return ""


@bp.route('/', methods=['GET'])
def list_paper():
    return ""
