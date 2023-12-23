#for use with google cloud functions
from flask import jsonify, Request, Response
import functions_framework
from library.activityFunctions import processActivity
from library.StravaAPI import getActivityById
from dataclasses import asdict


@functions_framework.http
def hello_http(request: Request) -> Response:

    if request.method == 'POST':
    
        activityID = request.args.get('activityID')

        activity = getActivityById(activityID)
        if activity.id == 0:
            return f"Activity {activityID} not found", 404

        _, hills = processActivity(activity.id)
        response = {
            "ActivityID": activity.id,
            "HillsClimbed": len(hills),
            "Hills": [asdict(hill) for hill in hills]
        }
    
        return jsonify(response), 200
    
    else:
        return f"{request.method} method not supported", 500
        
        
    
    

