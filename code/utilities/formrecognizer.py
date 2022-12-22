from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import os

def analyze_read(formUrl = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/rest-api/read.png"):

    document_analysis_client = DocumentAnalysisClient(
        endpoint=os.environ['Form_Recognizer_Endpoint'], credential=AzureKeyCredential(os.environ['Form_Recognizer_Key'])
    )
    
    poller = document_analysis_client.begin_analyze_document_from_url(
            "prebuilt-read", formUrl)
    result = poller.result()

    return result.content
  