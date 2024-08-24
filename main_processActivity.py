#for use with google cloud functions
from flask import jsonify, Request, Response
import functions_framework
from library.activityFunctions import processActivity
from library.StravaAPI import getActivityById, getActivities
from dataclasses import asdict
from data import config


@functions_framework.http
def hello_http(request: Request) -> Response:

    if request.method == 'POST':
        
        try:
            activityID = int(request.args.get('activityID'))
        except (TypeError, ValueError):
            return jsonify({"error": "No valid activityID supplied"}), 400      
        
        lastParsedActivity = config.get('last_parsed_activity')

        if activityID == 0: #Process latest activity 
            activity = getActivities(1,1)[0]
            
            if activity.id == lastParsedActivity:
                return jsonify({"ActivityID": activity.id, "message": "Latest activity already processed"}), 200
            
        else:
            activity = getActivityById(activityID)
            if not activity:
                return jsonify({"error": f"Activity {activityID} not found"}), 404

        _, hills = processActivity(activity.id)

        if activity.id > lastParsedActivity:
            config.write('last_parsed_activity', activity.id)
        
        response = {
            "ActivityID": activity.id,
            "HillsClimbed": len(hills),
            "Hills": [asdict(hill) for hill in hills]
        }
    
        return jsonify(response), 200
    
    else:
        return jsonify({"error": f"{request.method} method not supported"}), 500
        
        
    
    

