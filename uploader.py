import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
import uuid

cred = credentials.Certificate('./ein-server-firebase-adminsdk-key.json')
firebase_app = firebase_admin.initialize_app(cred, {
    'storageBucket': 'ein-server.appspot.com'
})
bucket = storage.bucket()


def upload_blob(source_file):
    destination_blob_name = str(uuid.uuid4())
    full_path ='f-g-images/' + destination_blob_name
    blob = bucket.blob(full_path)
    blob.upload_from_filename(source_file)
    blob.make_public()
    print(
        "File {} uploaded.".format(
            destination_blob_name
        )
    )
    return 'https://storage.googleapis.com/ein-server.appspot.com/'+full_path
