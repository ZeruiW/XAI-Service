
import os
import json
import uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import traceback


class AZ():

    def __init__(self, container='public', domain='https://xaifw.blob.core.windows.net') -> None:

        self.container = container
        self.domain = domain

        connection_str_path = os.path.join(
            os.environ['COMPONENT_TMP_DIR'], 'connection_str.json')

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
        except Exception:
            traceback.print_exc()

    def upload_blob(self, blob_file_name, sample_save_path, sample_metadata):
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container, blob=blob_file_name)

        # Upload the created file
        with open(file=sample_save_path, mode="rb") as data:
            blob_client.upload_blob(
                data,
                metadata={k: str(v) for k, v in sample_metadata.items()},
                overwrite=True)

    def list_blobs(self, sample_data_set, sample_group):

        container_client = self.blob_service_client.get_container_client(
            'public')

        blobs = []
        for blob in container_client.list_blobs(
                name_starts_with=f'{sample_data_set}/{sample_group}', include=['metadata']):
            blobs.append({
                'name': blob.name.replace(f'{sample_data_set}/{sample_group}', ''),
                # https://xaifw.blob.core.windows.net/public/imagenet1000/g0/ILSVRC2012_val_00049886.JPEG
                'address': f'{self.domain}/{self.container}/{blob.name}',
                'metadata': blob.metadata
            })

        return blobs
