from flask import jsonify, Request, Response
import functions_framework
from library.activityFunctions import processActivity
from library.StravaAPI import getActivityById, getActivities
from dataclasses import asdict
from data import config
from http import HTTPStatus
from data import userDAO


@functions_framework.http
def hello_http(request: Request) -> tuple[Response, HTTPStatus]:

    if request.method == 'POST':
        
        try:
            activityID = int(request.args.get('activityID'))
            athleteID = int(request.args.get('athleteID'))
        except (TypeError, ValueError):
            return jsonify({"error": "No valid activityID or athleteID supplied"}), HTTPStatus.BAD_REQUEST      
        
        lastParsedActivity = config.get('last_parsed_activity')

        user = userDAO.getUser(athleteId=athleteID)

        if activityID == 0: #Process latest activity 
            activity = getActivities(user, 1, 1)[0]
            
            if activity.id == lastParsedActivity:
                return jsonify({"ActivityID": activity.id, "message": "Latest activity already processed"}), 200
            
        else:
            activity = getActivityById(user, activityID)
            if not activity:
                return jsonify({"error": f"Activity {activityID} not found"}), HTTPStatus.NOT_FOUND

        _, hills = processActivity(activity.id, user)

        if activity.id > lastParsedActivity:
            config.write('last_parsed_activity', activity.id)
        
        response = {
            "ActivityID": activity.id,
            "HillsClimbed": len(hills),
            "Hills": [asdict(hill) for hill in hills]
        }
    
        return jsonify(response), HTTPStatus.OK
    
    else:
        return jsonify({"error": f"{request.method} method not supported"}), HTTPStatus.BAD_REQUEST
        
        
    
    

