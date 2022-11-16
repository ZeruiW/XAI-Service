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
    host="xaifwdb.c0gj2xdlz1ck.us-east-2.rds.amazonaws.com",
    user="root",
    password="xaidb.2022",
    database="xaifw"
)


@bp.route('/', methods=['POST'])
def upload_paper():
    return ""


@bp.route('/', methods=['GET'])
def list_paper():
    return ""
