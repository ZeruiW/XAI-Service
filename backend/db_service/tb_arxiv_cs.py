from base64 import encodebytes
import io
import json
import mysql.connector
from flask import (
    Blueprint, request, jsonify
)
from PIL import Image
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

MYSQL_HOST=os.getenv('MYSQL_HOST')
MYSQL_USER=os.getenv('MYSQL_USER')
MYSQL_PASSWORD=os.getenv('MYSQL_PASSWORD')
MYSQL_DB=os.getenv('MYSQL_DB')

bp = Blueprint('arxiv_cs', __name__, url_prefix='/db/arxiv_cs')

cnx = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
)


@bp.route('/', methods=['POST'])
def upload_paper():
    return ""


@bp.route('/', methods=['GET'])
def list_paper():
    return ""
