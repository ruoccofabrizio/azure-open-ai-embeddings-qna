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
    results = [x.content for x in result.paragraphs if x.role not in ['title', 'sectionHeading', 'footnote', 'pageHeader', 'pageFooter', 'pageNumber']]
    if translate_enabled:
        content_en = translate(result.content)
    else:
        content_en = result.content
    return content_en
    
#Translates text (if not english) -- Possible improvement: checkbox to let user decide if they want to translate
def translate(text):
    # Detect if it is not english
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
        # Translate to english

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
