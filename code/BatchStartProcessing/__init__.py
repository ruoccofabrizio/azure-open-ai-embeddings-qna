import logging, json, os
import azure.functions as func
from azure.storage.queue import QueueClient, BinaryBase64EncodePolicy
from utilities.azureblobstorage import get_all_files

account_name = os.environ['BLOB_ACCOUNT_NAME']
account_key = os.environ['BLOB_ACCOUNT_KEY']
connect_str = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
container_name = os.environ['BLOB_CONTAINER_NAME']
queue_name = os.environ['QUEUE_NAME']

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Requested to start processing all documents received')
    files_data = get_all_files()
    files_data = list(filter(lambda x : not x['embeddings_added'], files_data))
    files_data = list(map(lambda x: {'filename': x['filename']}, files_data))
    # Create the QueueClient object
    queue_client = QueueClient.from_connection_string(connect_str, queue_name, message_encode_policy=BinaryBase64EncodePolicy())
    # Send a message to the queue for each file
    for fd in files_data:
        queue_client.send_message(json.dumps(fd).encode('utf-8'))
 
    return func.HttpResponse(f"Conversion started successfully for {len(files_data)} documents.", status_code=200)