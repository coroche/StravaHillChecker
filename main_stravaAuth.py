#for use with google cloud functions
from flask import Request, Response, render_template_string
import functions_framework
from firebase_admin import auth as firebase_auth
from data import userDAO, config
from library.StravaAPI import TokenResponse
from data.config import getHTMLTemplate
from library import StravaAPI

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
        
        success, response_message = StravaAPI.deauthorise(user)
        
        if not success:
            return Response(f'unlink denied: {response_message}', 400)
        
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
    
    success, data = StravaAPI.authorise(user, code)
    if not success:
        user.setStravaConnectionData(linkStatus=userDAO.StravaLinkStatus.Denied)
        return Response('link denied', 401)
    
    tokens = TokenResponse(**data)
    athleteId = data['athlete']['id']
    user.updateStravaTokens(tokens.access_token, tokens.refresh_token, tokens.expires_in)
    user.setStravaConnectionData(athleteId=athleteId, scopes=scope_list, linkStatus=userDAO.StravaLinkStatus.Connected)
    message = render_template_string(getHTMLTemplate('message.html'), message = 'Strava connected successfully! You can close this tab.', script = 'window.close()')
    return Response(message, 200)
    

    



