# This class reads in the json file from blob and uses this
#  to deterime how many questions are available to fetch and what the first and last episode loaded were
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import json

class IndexSettings:
    def __init__(self):
        credential = DefaultAzureCredential()
        blob_url = 'https://jeopardysettings.blob.core.windows.net/dbsettings/history.json'
        blob_service_client = BlobServiceClient(account_url="https://jeopardysettings.blob.core.windows.net", credential=credential)
        blob_client = blob_service_client.get_blob_client(container="dbsettings", blob="history.json")

        self._blob_client = blob_client
        self.settings = None
        self.load_settings()

    def load_settings(self):
        blob_content = self._blob_client.download_blob().readall()
        self.settings = json.loads(blob_content)

    def get_highest_index(self):
        return self.settings.get('highest_read', 0)
    
    def get_lowest_index(self):
        return self.settings.get('lowest_read', 0)

    def get_question_count(self):
        return self.settings.get('question_count', 0)

    def get_prev_id(self):
        return self.settings.get('prev_id', None)

    def get_next_id(self):
        return self.settings.get('next_id', None)

    def update_settings(self, highest_index, lowest_index, question_count, prev_id, next_id):
        self.settings['highest_read'] = highest_index
        self.settings['lowest_read'] = lowest_index
        self.settings['question_count'] = question_count
        self.settings['prev_id'] = prev_id
        self.settings['next_id'] = next_id
        self.upload_settings()

    def upload_settings(self):
        self._blob_client.upload_blob(json.dumps(self.settings), overwrite=True)