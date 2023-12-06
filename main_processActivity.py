#for use with google cloud functions
from flask import jsonify, Request, Response
import functions_framework
import activityFunctions


@functions_framework.http
def hello_http(request: Request) -> Response:


    #Event notification
    if request.method == 'POST':
    
        activityID = request.args.get('activityID')
        _,_ = activityFunctions.processActivity(activityID)
    
        return f"Activity {activityID} processed", 200
    
    else:
        return f"{request.method} method not supported", 500
        
        
    
    

