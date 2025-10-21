import logging
import requests
import os
import azure.functions as func
import json

# Get your secret credentials from the Function App's "Configuration" settings
# This is the secure way to store secrets.
PREDICTION_ENDPOINT = os.environ.get("PREDICTION_ENDPOINT")
PREDICTION_KEY = os.environ.get("PREDICTION_KEY")

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Check if the secret keys are configured
    if not PREDICTION_ENDPOINT or not PREDICTION_KEY:
        return func.HttpResponse(
             "ERROR: Application is not configured. PREDICTION_ENDPOINT or PREDICTION_KEY is missing.",
             status_code=500
        )

    try:
        # Get the image data from the incoming request from the user's browser
        image_data = req.get_body()
        if not image_data:
            return func.HttpResponse("Please pass image data in the request body", status_code=400)

        # Prepare the headers for the call to the actual Azure AI Vision model
        headers = {
            'Prediction-Key': PREDICTION_KEY,
            'Content-Type': 'application/octet-stream'
        }

        # Make the secure, server-to-server request to the AI model
        response = requests.post(PREDICTION_ENDPOINT, headers=headers, data=image_data)
        response.raise_for_status() # This will raise an error for non-200 responses
        
        prediction_result = response.json()
        
        # Extract the top prediction if it exists
        if prediction_result and prediction_result.get('predictions'):
            top_prediction = prediction_result['predictions'][0]
            
            # Prepare the clean, simple response to send back to the user's browser
            result = {
                "sign": top_prediction.get("tagName", "?"),
                "confidence": top_prediction.get("probability", 0)
            }
        else:
            result = {"sign": "?", "confidence": 0}
        
        # Send the final result back to the user
        return func.HttpResponse(
            body=json.dumps(result),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return func.HttpResponse(
             "An error occurred during prediction.",
             status_code=500
        )

