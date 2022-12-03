from base64 import encodebytes
from flask import (
    Blueprint, request, jsonify, g
)

bp = Blueprint('arxiv_cs', __name__, url_prefix='/db/arxiv_cs')


@bp.route('/', methods=['POST'])
def upload_paper():
    return ""


@bp.route('/', methods=['GET'])
def list_paper():
    return ""
