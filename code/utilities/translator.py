import os, requests, urllib

def translate(text, language='en'):
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
    if (response[0]['language'] != language):
        endpoint_translate = os.environ['TRANSLATE_ENDPOINT'] + "/translate?api-version=3.0"
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
    

def get_available_languages():
    r = requests.get("https://api.cognitive.microsofttranslator.com/languages?api-version=3.0&scope=translation")
    # languages = sorted([{v['name']: k} for k,v in r.json()['translation'].items()], key=lambda x: list(x.keys())[0])
    languages = {}
    for k,v  in r.json()['translation'].items():
        languages[v['name']] =  k
    return languages