#for use with google cloud functions
from flask import jsonify, Request, Response
import functions_framework
from library.activityFunctions import processActivity
from data import config
from library.StravaAPI import getActivities
from dataclasses import asdict


@functions_framework.http
def hello_http(request: Request) -> Response:

    if request.method == 'POST':
    
        latestActivityID = getActivities(1,1)[0].id
        lastParsedActivity = config.get('last_parsed_activity')

        if latestActivityID == lastParsedActivity:
            return f"Activity {latestActivityID} already processed", 200
        
        else:

            _, hills = processActivity(latestActivityID)
            config.write('last_parsed_activity', latestActivityID)
            response = {
                "ActivityID": latestActivityID,
                "HillsClimbed": len(hills),
                "Hills": [asdict(hill) for hill in hills]
            }
        
            return jsonify(response), 200
    
    else:
        return f"{request.method} method not supported", 500
        
        
    
    

