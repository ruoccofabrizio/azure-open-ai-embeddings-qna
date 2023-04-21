import os, requests, urllib
from dotenv import load_dotenv

default_languages = {"translation":{"af":{"name":"Afrikaans","nativeName":"Afrikaans","dir":"ltr"},"am":{"name":"Amharic","nativeName":"አማርኛ","dir":"ltr"},"ar":{"name":"Arabic","nativeName":"العربية","dir":"rtl"},"as":{"name":"Assamese","nativeName":"অসমীয়া","dir":"ltr"},"az":{"name":"Azerbaijani","nativeName":"Azərbaycan","dir":"ltr"},"ba":{"name":"Bashkir","nativeName":"Bashkir","dir":"ltr"},"bg":{"name":"Bulgarian","nativeName":"Български","dir":"ltr"},"bn":{"name":"Bangla","nativeName":"বাংলা","dir":"ltr"},"bo":{"name":"Tibetan","nativeName":"བོད་སྐད་","dir":"ltr"},"bs":{"name":"Bosnian","nativeName":"Bosnian","dir":"ltr"},"ca":{"name":"Catalan","nativeName":"Català","dir":"ltr"},"cs":{"name":"Czech","nativeName":"Čeština","dir":"ltr"},"cy":{"name":"Welsh","nativeName":"Cymraeg","dir":"ltr"},"da":{"name":"Danish","nativeName":"Dansk","dir":"ltr"},"de":{"name":"German","nativeName":"Deutsch","dir":"ltr"},"dsb":{"name":"Lower Sorbian","nativeName":"Dolnoserbšćina","dir":"ltr"},"dv":{"name":"Divehi","nativeName":"ދިވެހިބަސް","dir":"rtl"},"el":{"name":"Greek","nativeName":"Ελληνικά","dir":"ltr"},"en":{"name":"English","nativeName":"English","dir":"ltr"},"es":{"name":"Spanish","nativeName":"Español","dir":"ltr"},"et":{"name":"Estonian","nativeName":"Eesti","dir":"ltr"},"eu":{"name":"Basque","nativeName":"Euskara","dir":"ltr"},"fa":{"name":"Persian","nativeName":"فارسی","dir":"rtl"},"fi":{"name":"Finnish","nativeName":"Suomi","dir":"ltr"},"fil":{"name":"Filipino","nativeName":"Filipino","dir":"ltr"},"fj":{"name":"Fijian","nativeName":"Na Vosa Vakaviti","dir":"ltr"},"fo":{"name":"Faroese","nativeName":"Føroyskt","dir":"ltr"},"fr":{"name":"French","nativeName":"Français","dir":"ltr"},"fr-CA":{"name":"French (Canada)","nativeName":"Français (Canada)","dir":"ltr"},"ga":{"name":"Irish","nativeName":"Gaeilge","dir":"ltr"},"gl":{"name":"Galician","nativeName":"Galego","dir":"ltr"},"gom":{"name":"Konkani","nativeName":"Konkani","dir":"ltr"},"gu":{"name":"Gujarati","nativeName":"ગુજરાતી","dir":"ltr"},"ha":{"name":"Hausa","nativeName":"Hausa","dir":"ltr"},"he":{"name":"Hebrew","nativeName":"עברית","dir":"rtl"},"hi":{"name":"Hindi","nativeName":"हिन्दी","dir":"ltr"},"hr":{"name":"Croatian","nativeName":"Hrvatski","dir":"ltr"},"hsb":{"name":"Upper Sorbian","nativeName":"Hornjoserbšćina","dir":"ltr"},"ht":{"name":"Haitian Creole","nativeName":"Haitian Creole","dir":"ltr"},"hu":{"name":"Hungarian","nativeName":"Magyar","dir":"ltr"},"hy":{"name":"Armenian","nativeName":"Հայերեն","dir":"ltr"},"id":{"name":"Indonesian","nativeName":"Indonesia","dir":"ltr"},"ig":{"name":"Igbo","nativeName":"Ásụ̀sụ́ Ìgbò","dir":"ltr"},"ikt":{"name":"Inuinnaqtun","nativeName":"Inuinnaqtun","dir":"ltr"},"is":{"name":"Icelandic","nativeName":"Íslenska","dir":"ltr"},"it":{"name":"Italian","nativeName":"Italiano","dir":"ltr"},"iu":{"name":"Inuktitut","nativeName":"ᐃᓄᒃᑎᑐᑦ","dir":"ltr"},"iu-Latn":{"name":"Inuktitut (Latin)","nativeName":"Inuktitut (Latin)","dir":"ltr"},"ja":{"name":"Japanese","nativeName":"日本語","dir":"ltr"},"ka":{"name":"Georgian","nativeName":"ქართული","dir":"ltr"},"kk":{"name":"Kazakh","nativeName":"Қазақ Тілі","dir":"ltr"},"km":{"name":"Khmer","nativeName":"ខ្មែរ","dir":"ltr"},"kmr":{"name":"Kurdish (Northern)","nativeName":"Kurdî (Bakur)","dir":"ltr"},"kn":{"name":"Kannada","nativeName":"ಕನ್ನಡ","dir":"ltr"},"ko":{"name":"Korean","nativeName":"한국어","dir":"ltr"},"ku":{"name":"Kurdish (Central)","nativeName":"Kurdî (Navîn)","dir":"rtl"},"ky":{"name":"Kyrgyz","nativeName":"Кыргызча","dir":"ltr"},"ln":{"name":"Lingala","nativeName":"Lingála","dir":"ltr"},"lo":{"name":"Lao","nativeName":"ລາວ","dir":"ltr"},"lt":{"name":"Lithuanian","nativeName":"Lietuvių","dir":"ltr"},"lug":{"name":"Ganda","nativeName":"Ganda","dir":"ltr"},"lv":{"name":"Latvian","nativeName":"Latviešu","dir":"ltr"},"lzh":{"name":"Chinese (Literary)","nativeName":"中文 (文言文)","dir":"ltr"},"mai":{"name":"Maithili","nativeName":"Maithili","dir":"ltr"},"mg":{"name":"Malagasy","nativeName":"Malagasy","dir":"ltr"},"mi":{"name":"Māori","nativeName":"Te Reo Māori","dir":"ltr"},"mk":{"name":"Macedonian","nativeName":"Македонски","dir":"ltr"},"ml":{"name":"Malayalam","nativeName":"മലയാളം","dir":"ltr"},"mn-Cyrl":{"name":"Mongolian (Cyrillic)","nativeName":"Mongolian (Cyrillic)","dir":"ltr"},"mn-Mong":{"name":"Mongolian (Traditional)","nativeName":"ᠮᠣᠩᠭᠣᠯ ᠬᠡᠯᠡ","dir":"ltr"},"mr":{"name":"Marathi","nativeName":"मराठी","dir":"ltr"},"ms":{"name":"Malay","nativeName":"Melayu","dir":"ltr"},"mt":{"name":"Maltese","nativeName":"Malti","dir":"ltr"},"mww":{"name":"Hmong Daw","nativeName":"Hmong Daw","dir":"ltr"},"my":{"name":"Myanmar (Burmese)","nativeName":"မြန်မာ","dir":"ltr"},"nb":{"name":"Norwegian","nativeName":"Norsk Bokmål","dir":"ltr"},"ne":{"name":"Nepali","nativeName":"नेपाली","dir":"ltr"},"nl":{"name":"Dutch","nativeName":"Nederlands","dir":"ltr"},"nso":{"name":"Sesotho sa Leboa","nativeName":"Sesotho sa Leboa","dir":"ltr"},"nya":{"name":"Nyanja","nativeName":"Nyanja","dir":"ltr"},"or":{"name":"Odia","nativeName":"ଓଡ଼ିଆ","dir":"ltr"},"otq":{"name":"Querétaro Otomi","nativeName":"Hñähñu","dir":"ltr"},"pa":{"name":"Punjabi","nativeName":"ਪੰਜਾਬੀ","dir":"ltr"},"pl":{"name":"Polish","nativeName":"Polski","dir":"ltr"},"prs":{"name":"Dari","nativeName":"دری","dir":"rtl"},"ps":{"name":"Pashto","nativeName":"پښتو","dir":"rtl"},"pt":{"name":"Portuguese (Brazil)","nativeName":"Português (Brasil)","dir":"ltr"},"pt-PT":{"name":"Portuguese (Portugal)","nativeName":"Português (Portugal)","dir":"ltr"},"ro":{"name":"Romanian","nativeName":"Română","dir":"ltr"},"ru":{"name":"Russian","nativeName":"Русский","dir":"ltr"},"run":{"name":"Rundi","nativeName":"Rundi","dir":"ltr"},"rw":{"name":"Kinyarwanda","nativeName":"Kinyarwanda","dir":"ltr"},"sd":{"name":"Sindhi","nativeName":"سنڌي","dir":"ltr"},"si":{"name":"Sinhala","nativeName":"සිංහල","dir":"ltr"},"sk":{"name":"Slovak","nativeName":"Slovenčina","dir":"ltr"},"sl":{"name":"Slovenian","nativeName":"Slovenščina","dir":"ltr"},"sm":{"name":"Samoan","nativeName":"Gagana Sāmoa","dir":"ltr"},"sn":{"name":"Shona","nativeName":"chiShona","dir":"ltr"},"so":{"name":"Somali","nativeName":"Soomaali","dir":"ltr"},"sq":{"name":"Albanian","nativeName":"Shqip","dir":"ltr"},"sr-Cyrl":{"name":"Serbian (Cyrillic)","nativeName":"Српски (ћирилица)","dir":"ltr"},"sr-Latn":{"name":"Serbian (Latin)","nativeName":"Srpski (latinica)","dir":"ltr"},"st":{"name":"Sesotho","nativeName":"Sesotho","dir":"ltr"},"sv":{"name":"Swedish","nativeName":"Svenska","dir":"ltr"},"sw":{"name":"Swahili","nativeName":"Kiswahili","dir":"ltr"},"ta":{"name":"Tamil","nativeName":"தமிழ்","dir":"ltr"},"te":{"name":"Telugu","nativeName":"తెలుగు","dir":"ltr"},"th":{"name":"Thai","nativeName":"ไทย","dir":"ltr"},"ti":{"name":"Tigrinya","nativeName":"ትግር","dir":"ltr"},"tk":{"name":"Turkmen","nativeName":"Türkmen Dili","dir":"ltr"},"tlh-Latn":{"name":"Klingon (Latin)","nativeName":"Klingon (Latin)","dir":"ltr"},"tlh-Piqd":{"name":"Klingon (pIqaD)","nativeName":"Klingon (pIqaD)","dir":"ltr"},"tn":{"name":"Setswana","nativeName":"Setswana","dir":"ltr"},"to":{"name":"Tongan","nativeName":"Lea Fakatonga","dir":"ltr"},"tr":{"name":"Turkish","nativeName":"Türkçe","dir":"ltr"},"tt":{"name":"Tatar","nativeName":"Татар","dir":"ltr"},"ty":{"name":"Tahitian","nativeName":"Reo Tahiti","dir":"ltr"},"ug":{"name":"Uyghur","nativeName":"ئۇيغۇرچە","dir":"rtl"},"uk":{"name":"Ukrainian","nativeName":"Українська","dir":"ltr"},"ur":{"name":"Urdu","nativeName":"اردو","dir":"rtl"},"uz":{"name":"Uzbek (Latin)","nativeName":"Uzbek (Latin)","dir":"ltr"},"vi":{"name":"Vietnamese","nativeName":"Tiếng Việt","dir":"ltr"},"xh":{"name":"Xhosa","nativeName":"isiXhosa","dir":"ltr"},"yo":{"name":"Yoruba","nativeName":"Èdè Yorùbá","dir":"ltr"},"yua":{"name":"Yucatec Maya","nativeName":"Yucatec Maya","dir":"ltr"},"yue":{"name":"Cantonese (Traditional)","nativeName":"粵語 (繁體)","dir":"ltr"},"zh-Hans":{"name":"Chinese Simplified","nativeName":"中文 (简体)","dir":"ltr"},"zh-Hant":{"name":"Chinese Traditional","nativeName":"繁體中文 (繁體)","dir":"ltr"},"zu":{"name":"Zulu","nativeName":"Isi-Zulu","dir":"ltr"}}}

class AzureTranslatorClient:
    def __init__(self, translate_key=None, translate_region=None, translate_endpoint=None):

        load_dotenv()

        self.translate_key = translate_key if translate_key else os.getenv('TRANSLATE_KEY')
        self.translate_region = translate_region if translate_region else os.getenv('TRANSLATE_REGION')
        self.translate_endpoint = translate_endpoint if translate_endpoint else os.getenv('TRANSLATE_ENDPOINT')
        self.api_version = "3.0"

        if os.getenv('VNET_DEPLOYMENT', 'false') == 'false':
            self.detect_endpoint = urllib.parse.urljoin(self.translate_endpoint, f"/detect?api-version={self.api_version}")
            self.translate_endpoint = urllib.parse.urljoin(self.translate_endpoint, f"/translate?api-version={self.api_version}")
        else:
            self.detect_endpoint = urllib.parse.urljoin(self.translate_endpoint, f"/translator/text/v3.0/detect?api-version={self.api_version}")
            self.translate_endpoint = urllib.parse.urljoin(self.translate_endpoint, f"/translator/text/v3.0/translate?api-version={self.api_version}")


    def translate(self, text, language='en'):
        headers = {
            'Ocp-Apim-Subscription-Key': self.translate_key,
            'Ocp-Apim-Subscription-Region': self.translate_region,
            'Content-type': 'application/json'
        }
        params = urllib.parse.urlencode({})
        body = [{
            'text': text
        }]
        request = requests.post(self.detect_endpoint, params=params, headers=headers, json=body)
        response = request.json()
        if (response[0]['language'] != language):
            params = urllib.parse.urlencode({
                'from': response[0]['language'],
                'to': language
            })
            body = [{
                'text': text
            }]
            request = requests.post(self.translate_endpoint, params=params, headers=headers, json=body)
            response = request.json()
            return response[0]['translations'][0]['text']
        else:
            return text
        

    def get_available_languages(self):
        if os.getenv('VNET_DEPLOYMENT', 'false') == 'true':
            available_languages = default_languages['translation']
        else:
            r = requests.get(f"https://api.cognitive.microsofttranslator.com/languages?api-version={self.api_version}&scope=translation")
            available_languages = r.json()['translation']
        languages = {}
        for k,v  in available_languages.items():
            languages[v['name']] =  k
        return languages