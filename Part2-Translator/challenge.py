from dotenv import load_dotenv
import os
import requests

def main():
    try:
        # Get Configuration Settings
        load_dotenv()
        key = os.getenv('COG_SERVICE_KEY')
        region = os.getenv('COG_SERVICE_REGION')
        endpoint = 'https://api.cognitive.microsofttranslator.com'

        text = 'Hello world!'
        print('Detected language of "' + text + '":', detect_language(text, key, region, endpoint))
        target_lang = ['el','de','fr','it','th']
        results = translate(text, 'en', target_lang, key, region, endpoint)
        for i in range(len(results)):
            print(target_lang[i] + ":", results[i])
    except Exception as ex:
        print(ex)

def detect_language(text, key, region, endpoint):
    # Use the Translator detect function
    path = '/detect'
    url = endpoint + path
    # Build the request
    params = {
        'api-version': '3.0'
    }
    headers = {
    'Ocp-Apim-Subscription-Key': key,
    'Ocp-Apim-Subscription-Region': region,
    'Content-type': 'application/json'
    }
    body = [{
        'text': text
    }]
    # Send the request and get response
    request = requests.post(url, params=params, headers=headers, json=body)
    response = request.json()
    # Get language
    language = response[0]["language"]
    # Return the language
    return language

def translate(text, source_language, target_language, key, region, endpoint):
    # Use the Translator translate function
    url = endpoint + '/translate'
    # Build the request
    params = {
        'api-version': '3.0',
        'from': source_language,
        'to': target_language
    }
    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': region,
        'Content-type': 'application/json'
    }
    body = [{
        'text': text
    }]
    # Send the request and get response
    request = requests.post(url, params=params, headers=headers, json=body)
    response = request.json()
    # Get translation
    translation = []
    translations = response[0]["translations"]
    for t in translations:
        translation.append(t['text'])
    # Return the translation
    return translation

if __name__ == "__main__":
    main()