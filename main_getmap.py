from flask import Flask,request, render_template, redirect, url_for
from data.config import getEmailTemplate
from data import config
from library.smtp import sendEmail
from library.googleSheetsAPI import getPeaks, login, buildService, Hill
from data.config import getConfig
import json

app = Flask(__name__)

def createMapLocationDict(peak: Hill) -> dict:
    cat, done = 'VL','' 
    if peak.done:
        done = 'Done'
    if peak.Highest100:
        cat = 'HighestHundred'
    actions = []
    if peak.ActivityID:
        actions = [{"label":"Open Strava Activity","defaultUrl":f"https://www.strava.com/activities/{peak.ActivityID}"}]
    
    d = {
        "title":peak.name,
        "area":f"Area: {peak.Area}",
        "height":f"Height: {peak.Height}",
        "coords":{"lat":peak.latitude,"lng":peak.longitude},
        "actions":actions,
        "icon": f"{cat}{done}Icon",
        "bigicon": f"{cat}{done}Icon_selected"
        }
    return d

def serve_form():
    creds = login()
    service = buildService(creds)
    settings = getConfig()
    
    peaks = getPeaks(settings.google_script_ID, service)
    peaks_dict = [createMapLocationDict(peak) for peak in peaks]
    json_data = json.dumps(peaks_dict)
    js_list_content = f'"locations": {json_data},'

    html = getEmailTemplate('map.html')
    html = html\
        .replace('<!-- Add location list here -->', js_list_content)\
        .replace('{{APIToken}}', settings.google_maps_api_key)

    return html



def gcf_entry_point(request):

    return serve_form()