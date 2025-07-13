#for use with google cloud functions
from flask import Request, Response, render_template_string
import functions_framework
from firebase_admin import auth as firebase_auth
from data import userDAO, config
import requests
import json
from library.StravaAPI import TokenResponse
from data.config import getHTMLTemplate

settings = config.getConfig()


@functions_framework.http
def gcf_entry_point(request: Request) -> Response:
    
    token = request.args.get('state')
    if not token:
        return Response('link denied', 400)
    
    try:
        decoded = firebase_auth.verify_id_token(token)
        uid = decoded['uid']
    except Exception:
        return Response('link denied', 401)
    user = userDAO.getBasicUser(userId=uid)
    if not user:
        return Response('link denied', 401)
    
    deauthorise = request.args.get('deauthorise')
    if deauthorise:
        
        url = f'https://www.strava.com/oauth/deauthorize?access_token={user.strava_access_token}'
        response = requests.post(url)
        
        if response.status_code != 200:
            return Response(f'unlink denied: {response.text}', 400)
        
        user.removeStravaConnectionData()
        message = render_template_string(getHTMLTemplate('message.html'), message = 'Strava disconnected successfully! You can close this tab.', script = 'window.close()')
        return Response(message, 200)
   
    
    code = request.args.get('code')
    if not code:
        return Response('link denied', 400)
    
    error = request.args.get('error')
    if error:
        user.setStravaConnectionData(linkStatus=userDAO.StravaLinkStatus.Denied)
        return Response('link denied', 401)
    
    scope = request.args.get('scope')
    scope_list = scope.split(',')
    


    url = 'https://www.strava.com/api/v3/oauth/token'

    payload={
        'client_id': settings.client_id,
        'client_secret': settings.client_secret,
        'code': code,
        'grant_type': 'authorization_code',
    }

    response = requests.request("POST", url, data=payload)
    if response.status_code != 200:
        user.setStravaConnectionData(linkStatus=userDAO.StravaLinkStatus.Denied)
        return Response('link denied', 401)
    
    response_data = json.loads(response.text)
    tokens = TokenResponse(**response_data)
    athleteId = response_data['athlete']['id']
    user.updateStravaTokens(tokens.access_token, tokens.refresh_token, tokens.expires_in)
    user.setStravaConnectionData(athleteId=athleteId, scopes=scope_list, linkStatus=userDAO.StravaLinkStatus.Connected)
    message = render_template_string(getHTMLTemplate('message.html'), message = 'Strava connected successfully! You can close this tab.', script = 'window.close()')
    return Response(message, 200)
    

    



