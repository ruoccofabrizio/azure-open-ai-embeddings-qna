import os, requests, urllib

def translate(text):
    endpoint_detect = os.environ['TRANSLATE_ENDPOINT'] + "/detect?api-version=3.0"
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
        return response[0]['translations'][0]['text']
    else:
        return text