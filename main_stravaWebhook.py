#for use with google cloud functions
from flask import jsonify, Request, Response
import functions_framework
from data import config
import concurrent.futures
import requests

executor = concurrent.futures.ThreadPoolExecutor()
settings = config.getConfig()

def callProcessActivity(activityID: int):
    url = f"{settings.google_functions_url}/processActivity?activityID={activityID}"
    requests.request("POST", url)


@functions_framework.http
def hello_http(request: Request) -> Response:

    request_json = request.get_json(silent=True)
    request_args = request.args

    #Event notification
    if request.method == 'POST':

        if request_json['object_type'] == 'activity':
            
            activityID = request_json['object_id']
            future = executor.submit(callProcessActivity, activityID)
        
            return f"Processing activity {activityID}", 200
        
        else:
            return "Not an activity", 200
    
    #Subscription verification
    elif request.method == 'GET':

        mode = request_args.get('hub.mode')
        token = request_args.get('hub.verify_token')
        challenge = request_args.get('hub.challenge')

        if mode == 'subscribe' and token == settings.webhook_verify_token:
            response = { "hub.challenge":challenge }
            return jsonify(response), 200
        else:
            return "Invalid request", 500
        
    else:
        return f"{request.method} method not supported", 500

