
import os
import io
from PIL import Image
from base64 import encodebytes
import json
import uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import traceback


def get_response_image(img_data):
    pil_img = Image.open(io.BytesIO(img_data)).convert(
        'RGB')  # reads the PIL image
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG')  # convert the PIL image to byte array
    encoded_img = encodebytes(byte_arr.getvalue()).decode(
        'ascii')  # encode as base64
    return encoded_img


class AZ():

    def __init__(self, container='public', domain='https://xaifw.blob.core.windows.net') -> None:

        self.container = container
        self.domain = domain

        connection_str_path = os.path.join(
            os.environ['COMPONENT_TMP_DIR'], 'az_blob_connection_str.json')

        if not os.path.exists(connection_str_path):
            print(f'Please provide azure blob connection key at: ',
                  connection_str_path)
            exit(1)

        with open(connection_str_path) as f:
            connection_str = json.load(f)['connection_str']

        try:
            # Quickstart code goes here
            # Create the BlobServiceClient object
            self.blob_service_client = BlobServiceClient.from_connection_string(
                connection_str)
            print("Azure Blob: Connected")
        except Exception:
            traceback.print_exc()

    def upload_blob(self, data, blob_file_name, sample_metadata):

        if sample_metadata == None:
            sample_metadata = {}

        blob_client = self.blob_service_client.get_blob_client(
            container=self.container, blob=blob_file_name)

        blob_client.upload_blob(
            data,
            metadata={k: str(v) for k, v in sample_metadata.items()},
            overwrite=True)

    def get_blobs(self, data_set_name, data_set_group_name, with_content=False):

        container_client = self.blob_service_client.get_container_client(
            'public')

        blobs = []
        for blob in container_client.list_blobs(
                name_starts_with=f'{data_set_name}/{data_set_group_name}', include=['metadata']):

            blob_rs = {
                'name': blob.name.replace(f'{data_set_name}/{data_set_group_name}/', ''),
                # https://xaifw.blob.core.windows.net/public/imagenet1000/g0/ILSVRC2012_val_00049886.JPEG
                'address': f'{self.domain}/{self.container}/{blob.name}',
                'metadata': blob.metadata
            }

            blob_name = blob['name']
            ext = blob_name.split('.')[-1]

            if with_content:
                if ext.lower() in ['png', 'jpeg']:
                    blob_rs['content'] = get_response_image(container_client.download_blob(
                        blob.name).readall())
                else:
                    byte_arr = io.BytesIO()
                    container_client.download_blob(
                        blob.name).readinto(byte_arr)
                    blob_rs['content'] = encodebytes(byte_arr.getvalue()).decode(
                        'ascii')
            blobs.append(blob_rs)
        return blobs

    def delete_blobs(self, name_starts_with):

        container_client = self.blob_service_client.get_container_client(
            'public')

        blobs = container_client.list_blobs(
            name_starts_with=name_starts_with)

        container_client.delete_blobs(*blobs, delete_snapshots='include')
