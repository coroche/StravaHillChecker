#for use with google cloud functions
from flask import jsonify, Request, Response
import functions_framework
from data import config
import concurrent.futures
import requests
from dataclasses import dataclass
from utils.decorators import trim

executor = concurrent.futures.ThreadPoolExecutor()
settings = config.getConfig()

@trim
@dataclass
class WebHookRequest:
    aspect_type: str
    object_id: int
    object_type: str
    owner_id: str
    updates: dict = None


def callProcessActivity(activityID: int, athleteID: int, deleteActivity: bool = False):
    delStr = ''
    if deleteActivity:
        delStr = '&deleteActivity=true'
    url = f"{settings.google_functions_url}/processActivity?activityID={activityID}&athleteID={athleteID}{delStr}"
    requests.request("POST", url)


@functions_framework.http
def hello_http(request: Request, testMode: bool = False) -> Response:

    #Event notification
    if request.method == 'POST':
        try:
            request_json = WebHookRequest(**request.get_json(silent=True))
        except (AttributeError, TypeError, ValueError):
            return "Invalid webhook notification format", 400
        
        if request_json.object_type != 'activity':
            return "Not an activity", 200
        
        activityID = request_json.object_id
        athleteID = request_json.owner_id
        activityUpdatedToPrivate = request_json.aspect_type == 'update' and request_json.updates.get('private', None) == 'true' 
        activityDeleted = request_json.aspect_type == 'delete'

        if activityUpdatedToPrivate or activityDeleted:
            future = executor.submit(callProcessActivity, activityID, athleteID, deleteActivity=True)
            if testMode:
                future.result()
            return f"Removing activity {activityID}", 200
        
        else:
            future = executor.submit(callProcessActivity, activityID, athleteID)
            if testMode:
                future.result()
            return f"Processing activity {activityID}", 200
            
    
    #Subscription verification
    elif request.method == 'GET':
        request_args = request.args

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

