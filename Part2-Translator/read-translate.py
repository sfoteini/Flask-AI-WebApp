from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
import time
from dotenv import load_dotenv
import os
import requests

def main():
    try:
        # Get Configuration Settings
        load_dotenv()
        key = os.getenv("COG_SERVICE_KEY")
        region = os.getenv("COG_SERVICE_REGION")
        endpoint = "https://api.cognitive.microsofttranslator.com"
        COG_endpoint = os.getenv("COG_SERVICE_ENDPOINT")
        # Authenticate Computer Vision client
        computervision_client = ComputerVisionClient(COG_endpoint, CognitiveServicesCredentials(key))

        # Analyze each image file in the images folder
        images_folder = os.path.join (os.path.dirname(os.path.abspath(__file__)), "images")
        for file_name in os.listdir(images_folder):
            # Extract text
            print("\n" + "="*12)
            read_image_path = os.path.join (images_folder, file_name)
            text = get_text(read_image_path, computervision_client)
            #print(text)
            
            # Detect the language
            language = detect_language(text, key, region, endpoint)
            print("Language:", language)
            
            # Translate
            target_lang = ["el"]
            results = translate(text, language, target_lang, key, region, endpoint)
            for i in range(len(results)):
                print("\n" + "-"*12)
                print(target_lang[i] + ":", results[i])
        
    except Exception as ex:
        print(ex)

def get_text(image_file, computervision_client):
    # Open local image file
    with open(image_file, "rb") as image:
        # Call the API
        read_response = computervision_client.read_in_stream(image, raw=True)

    # Get the operation location (URL with an ID at the end)
    read_operation_location = read_response.headers["Operation-Location"]
    # Grab the ID from the URL
    operation_id = read_operation_location.split("/")[-1]

    # Retrieve the results 
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status.lower() not in ["notstarted", "running"]:
            break
        time.sleep(1)

    # Get the detected text
    text = ""
    if read_result.status == OperationStatusCodes.succeeded:
        for page in read_result.analyze_result.read_results:
            for line in page.lines:
                # Get text in each detected line and do some fixes to the structure
                if (not text) or text[-1].strip() == "." or text[-1].strip() == ":":
                    text = text + "\n" + line.text
                else:
                    text = text + " " + line.text
    text = text.replace(" .", ".").replace(" ,", ",").replace(" :", ":")
    #print(text)
    return text

def detect_language(text, key, region, endpoint):
    # Use the Translator detect function
    path = "/detect"
    url = endpoint + path
    # Build the request
    params = {
        "api-version": "3.0"
    }
    headers = {
    "Ocp-Apim-Subscription-Key": key,
    "Ocp-Apim-Subscription-Region": region,
    "Content-type": "application/json"
    }
    body = [{
        "text": text
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
    url = endpoint + "/translate"
    # Build the request
    params = {
        "api-version": "3.0",
        "from": source_language,
        "to": target_language
    }
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Ocp-Apim-Subscription-Region": region,
        "Content-type": "application/json"
    }
    body = [{
        "text": text
    }]
    # Send the request and get response
    request = requests.post(url, params=params, headers=headers, json=body)
    response = request.json()
    # Get translation
    translation = []
    translations = response[0]["translations"]
    for t in translations:
        translation.append(t["text"])
    # Return the translation
    return translation

if __name__ == "__main__":
    main()