import os
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_blob_sas, generate_container_sas, ContentSettings

def upload_file(bytes_data, file_name, content_type='application/pdf'):
    account_name = os.environ['BLOB_ACCOUNT_NAME']
    account_key = os.environ['BLOB_ACCOUNT_KEY']
    connect_str = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
    container_name = os.environ['BLOB_CONTAINER_NAME']
    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
    # Upload the created file
    blob_client.upload_blob(bytes_data,overwrite=True, content_settings=ContentSettings(content_type=content_type))

    return blob_client.url + '?' + generate_blob_sas(account_name, container_name, file_name,account_key=account_key,  permission="r", expiry=datetime.utcnow() + timedelta(hours=3))

def get_all_files():
    # Get all files in the container from Azure Blob Storage
    account_name = os.environ['BLOB_ACCOUNT_NAME']
    account_key = os.environ['BLOB_ACCOUNT_KEY']
    connect_str = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
    container_name = os.environ['BLOB_CONTAINER_NAME']
    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    # Get files in the container
    container_client = blob_service_client.get_container_client(container_name)
    blob_list = container_client.list_blobs()
    # sas = generate_blob_sas(account_name, container_name, blob.name,account_key=account_key,  permission="r", expiry=datetime.utcnow() + timedelta(hours=3))
    sas = generate_container_sas(account_name, container_name,account_key=account_key,  permission="r", expiry=datetime.utcnow() + timedelta(hours=3))
    files = []
    converted_files = {}
    for blob in blob_list:
        if not blob.name.startswith('converted/'):
            files.append({
                "filename" : blob.name,
                "converted": False, 
                "fullpath": f"https://{account_name}.blob.core.windows.net/{container_name}/{blob.name}?{sas}",
                "converted_path": ""
                })
        else:
            converted_files[blob.name] = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob.name}?{sas}"

    for file in files:
        converted_filename = f"converted/{file['filename']}.txt"
        if converted_filename in converted_files:
            file['converted'] = True
            file['converted_path'] = converted_files[converted_filename]
    
    return files

def process_all_within_blob(translate_enabled):
    account_name = os.environ['BLOB_ACCOUNT_NAME']
    account_key = os.environ['BLOB_ACCOUNT_KEY']
    container_name = os.environ['BLOB_CONTAINER_NAME']
    connect_str = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)    
    container_client = blob_service_client.get_container_client(container_name)
    blob_list = container_client.list_blobs()
    sas = generate_container_sas(account_name, container_name,account_key=account_key,  permission="r", expiry=datetime.utcnow() + timedelta(hours=1))  
    for blob in blob_list:
        url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob.name}"
        blob_sas=url+'?'+sas
        # TO DO: check if already converted (in folder converted)
        if blob.name.endswith('.pdf') or blob.name.endswith('jpeg') or blob.name.endswith('jpg') or blob.name.endswith('png'):
            print('Processing sas url: ', blob_sas)
            text=analyze_ocr(blob_sas, translate_enabled)
            embeddings = chunk_and_embed(text)
            redisembeddings.set_document(embeddings)
            print('Embeddings added to redis for: ', blob.name)
