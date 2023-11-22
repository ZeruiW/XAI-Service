import io
from flask import (
    request, jsonify
)
from xai_backend_central_dev.flask_manager import ExecutorBluePrint
import requests
from dotenv import load_dotenv
import os

# 加载.env文件
load_dotenv("config.env")

API_URL = os.environ.get("API_URL")
HF_AUTH_TOKEN = os.environ.get("HF_AUTH_TOKEN")
headers = {"Authorization": f"Bearer {HF_AUTH_TOKEN}"}

ebp = ExecutorBluePrint(
    'hf_resnet50', __name__, component_path=__file__, url_prefix='/hf_resnet50')

def query(image_bytes):
    response = requests.post(API_URL, headers=headers, data=image_bytes)
    json_response = response.json()
    print(json_response)  # 打印响应以供调试
    return json_response


@ebp.route('/', methods=['POST'])
def pred():
    if request.method == 'POST':
        files = request.files
        imgs = files.getlist('image')
        file_name = [img.filename for img in imgs]
        imgs = [i.read() for i in imgs]

        rs = {}
        for i in range(len(file_name)):
            prediction = query(imgs[i])
            scores = [round(item['score'], 6) for item in prediction]
            labels = [item['label'] for item in prediction]
            rs[file_name[i]] = {'scores': scores, 'labels': labels}

        return jsonify(rs)

