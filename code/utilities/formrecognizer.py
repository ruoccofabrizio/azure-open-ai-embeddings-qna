from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import os, requests, urllib

def analyze_ocr(formUrl, translate_enabled=False):

    document_analysis_client = DocumentAnalysisClient(
        endpoint=os.environ['FORM_RECOGNIZER_ENDPOINT'], credential=AzureKeyCredential(os.environ['FORM_RECOGNIZER_KEY'])
    )
    
    poller = document_analysis_client.begin_analyze_document_from_url(
            "prebuilt-layout", formUrl)
    result = poller.result()
    results = ' '.join([x.content for x in result.paragraphs if x.role not in ['title', 'sectionHeading', 'footnote', 'pageHeader', 'pageFooter', 'pageNumber']])
    if translate_enabled:
        content_en = translate(results)
    else:
        content_en = results
    return content_en
    
def translate(text):
    endpoint_detect = os.environ['TRANSLATE_ENDPOINT'] + "/detect?api-version=3.0"
    endpoint_detect
    print ('Endpoint is ', endpoint_detect)
    headers = {
        'Ocp-Apim-Subscription-Key': os.environ['TRANSLATE_KEY'],
        'Ocp-Apim-Subscription-Region': os.environ['TRANSLATE_REGION'],
        'Content-type': 'application/json'
    }
    params = urllib.parse.urlencode({})
    body = [{
        'text': text
    }]
    request = requests.post(endpoint_detect, params=params, headers=headers, json=body)
    response = request.json()
    if response[0]['language'] != 'en':
        endpoint_translate = os.environ['TRANSLATE_ENDPOINT'] + "/translate?api-version=3.0"
        params = urllib.parse.urlencode({
            'api-version': '3.0',
            'from': response[0]['language'],
            'to': 'en'
        })
        body = [{
            'text': text
        }]
        request = requests.post(endpoint_translate, params=params, headers=headers, json=body)
        response = request.json()
        #print('Translated: ', request)
        return response[0]['translations'][0]['text']
    else:
        return text
