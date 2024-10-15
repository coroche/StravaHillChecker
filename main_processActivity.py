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
            return jsonify({"error": "Valid activityID and athleteID not supplied"}), HTTPStatus.BAD_REQUEST      
        
        deleteActivity = request.args.get('deleteActivity', '', str).lower() == 'true'
        user = userDAO.getUser(athleteId=athleteID)
        lastParsedActivity = config.get('last_parsed_activity')

        if deleteActivity:
            user.deleteActivity(activityID)
            return jsonify({"ActivityID": activityID, "message": "Activity removed from completed hills list"}), HTTPStatus.OK

        if activityID == 0: #Process latest activity 
            activity = getActivities(user, 1, 1)[0]
            
            if activity.id == lastParsedActivity:
                return jsonify({"ActivityID": activity.id, "message": "Latest activity already processed"}), HTTPStatus.OK
            
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
        
        
    
    

