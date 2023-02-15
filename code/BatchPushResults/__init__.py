import logging, json, os, io
import azure.functions as func
from azure.storage.blob import BlobServiceClient, generate_blob_sas
from datetime import datetime, timedelta
from utilities.formrecognizer import analyze_read
from utilities.azureblobstorage import upload_file, upsert_blob_metadata
from utilities.redisembeddings import set_document
from utilities.utils import chunk_and_embed
from utilities.utils import add_embeddings, convert_file_and_add_embeddings, initialize

account_name = os.environ['BLOB_ACCOUNT_NAME']
account_key = os.environ['BLOB_ACCOUNT_KEY']
connect_str = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
container_name = os.environ['BLOB_CONTAINER_NAME']

def main(msg: func.QueueMessage) -> None:
    logging.info('Python queue trigger function processed a queue item: %s',
                 msg.get_body().decode('utf-8'))

    # Set up Azure OpenAI connection
    initialize()

    # Get the file name from the message
    file_name = json.loads(msg.get_body().decode('utf-8'))['filename']

    # Check the file extension
    if file_name.endswith('.txt'):
        # Read the file from Blob Storage
        blob_client = BlobServiceClient.from_connection_string(connect_str).get_blob_client(container=container_name, blob=file_name)
        file_content = blob_client.download_blob().readall().decode('utf-8')

        # Embed the file
        data = chunk_and_embed(file_content, file_name)

        # Set the document in Redis
        set_document(data)
    else:
        file_sas = generate_blob_sas(account_name, container_name, file_name, account_key= account_key, permission='r', expiry=datetime.utcnow() + timedelta(hours=1))
        convert_file_and_add_embeddings(f"https://{account_name}.blob.core.windows.net/{container_name}/{file_name}?{file_sas}" , file_name)

    upsert_blob_metadata(file_name, {'embeddings_added': 'true'})