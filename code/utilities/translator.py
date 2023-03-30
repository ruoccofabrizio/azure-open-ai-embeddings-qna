import os, requests, urllib
from dotenv import load_dotenv

class AzureTranslatorClient:
    def __init__(self, translate_key=None, translate_region=None, translate_endpoint=None):

        load_dotenv()

        self.translate_key = translate_key if translate_key else os.getenv('TRANSLATE_KEY')
        self.translate_region = translate_region if translate_region else os.getenv('TRANSLATE_REGION')
        self.translate_endpoint = translate_endpoint if translate_endpoint else os.getenv('TRANSLATE_ENDPOINT')

    def translate(self, text, language='en'):
        endpoint_detect = os.environ['TRANSLATE_ENDPOINT'] + "/detect?api-version=3.0"
        headers = {
            'Ocp-Apim-Subscription-Key': self.translate_key,
            'Ocp-Apim-Subscription-Region': self.translate_region,
            'Content-type': 'application/json'
        }
        params = urllib.parse.urlencode({})
        body = [{
            'text': text
        }]
        request = requests.post(endpoint_detect, params=params, headers=headers, json=body)
        response = request.json()
        if (response[0]['language'] != language):
            endpoint_translate = self.translate_endpoint + "/translate?api-version=3.0"
            params = urllib.parse.urlencode({
                'api-version': '3.0',
                'from': response[0]['language'],
                'to': language
            })
            body = [{
                'text': text
            }]
            request = requests.post(endpoint_translate, params=params, headers=headers, json=body)
            response = request.json()
            return response[0]['translations'][0]['text']
        else:
            return text
        

    def get_available_languages(self):
        r = requests.get("https://api.cognitive.microsofttranslator.com/languages?api-version=3.0&scope=translation")
        languages = {}
        for k,v  in r.json()['translation'].items():
            languages[v['name']] =  k
        return languages