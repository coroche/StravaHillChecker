#for use with google cloud functions
from flask import jsonify, Request, Response
import functions_framework
import activityFunctions
import config

@functions_framework.http
def hello_http(request: Request) -> Response:

    request_json = request.get_json(silent=True)
    request_args = request.args

    #Event notification
    if request.method == 'POST':
        hillsFound = False
        if request_json['object_type'] == 'activity':
            hillsFound, _ = activityFunctions.processActivity(request_json['object_id'])
        
        response = { "hills_found": str(hillsFound) }
        return jsonify(response), 200
    
    #Subscription verification
    elif request.method == 'GET':
        settings = config.getConfig()

        mode = request_args.get('hub.mode')
        token = request_args.get('hub.verify_token')
        challenge = request_args.get('hub.challenge')

        if mode == 'subscribe' and token == settings.webhook_verify_token:
            response = { "hub.challenge":challenge }
            return jsonify(response), 200

