from flask import Flask, request, render_template
import requests, os, time
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes

app = Flask(__name__)

def get_text(image_url, computervision_client):
    # Open local image file
    read_response = computervision_client.read(image_url, raw=True)

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
    translation = response[0]["translations"][0]["text"]
    # Return the translation
    return translation

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def index_post():
    # Read the values from the form
    image_url = request.form['image']
    target_language = request.form['language']
    
    # Load the values from app settings
    key = os.environ["COG_SERVICE_KEY"]
    region = os.environ["COG_SERVICE_REGION"]
    endpoint = os.environ["ENDPOINT"]
    COG_endpoint = os.environ["COG_SERVICE_ENDPOINT"]
    
    # Authenticate Computer Vision client
    computervision_client = ComputerVisionClient(COG_endpoint, CognitiveServicesCredentials(key))

    # Extract text
    text = get_text(image_url, computervision_client)
    
    # Detect language
    language = detect_language(text, key, region, endpoint)

    # Translate text
    translated_text = translate(text, language, target_language, key, region, endpoint)

    # Call render template
    return render_template(
        'results.html',
        translated_text=translated_text,
        original_text=text,
        target_language=target_language
    )


if __name__ == '__main__':
    app.run(debug=True)