import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
import uuid

import config

cred = credentials.Certificate('./firebase-adminsdk-key.json')
firebase_app = firebase_admin.initialize_app(cred, {
    'storageBucket': config.storage_bucket
})
bucket = storage.bucket()


def upload_blob(source_file):
    destination_blob_name = str(uuid.uuid4())
    full_path = 'f-g-images/' + destination_blob_name
    blob = bucket.blob(full_path)
    blob.upload_from_filename(source_file)
    blob.make_public()
    url = 'https://storage.googleapis.com/{}/{}'.format(config.storage_bucket, full_path)
    print(url)
    return url
