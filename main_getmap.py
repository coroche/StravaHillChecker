from flask import Flask, Request, Response, render_template_string
from data.config import getHTMLTemplate, Config
from data.hillsDAO import Hill
from data.config import getConfig
from library.googleSheetsAPI import Hill as SheetsHill
import json
from data.userDAO import getUserHillList
from http import HTTPStatus
from dataclasses import asdict

app = Flask(__name__)

def createMapLocationDict(peak: Hill | SheetsHill, icon_bucket: str) -> dict:
    cat = 'Peak'
    if isinstance(peak, SheetsHill):
        cat = 'VL'
        if peak.Highest100:
            cat = 'HighestHundred'
    
    done = ''
    if peak.done:
            done = 'Done'
    actions = []
    if peak.ActivityID:
        actions = [{"label":"Strava","defaultUrl":f"https://www.strava.com/activities/{peak.ActivityID}"}]
    
    d = {
        "title":peak.name,
        "area":f"Area: {peak.Area}",
        "height":f"Height: {peak.Height}",
        "coords":{"lat":peak.latitude,"lng":peak.longitude},
        "actions":actions,
        "icon": f"{cat}{done}Icon",
        "bigicon": f"{cat}{done}Icon_selected",
        "iconsrc": f"{icon_bucket}/{cat}{done}.png"
        }
    return d


def serve_map(peaks: list[Hill] | list[SheetsHill], settings: Config) -> Response:
    peaks_dict = [createMapLocationDict(peak, settings.map_icon_bucket) for peak in peaks]
    json_data = json.dumps(peaks_dict)
    js_list_content = f'"locations": {json_data},'

    html = getHTMLTemplate('map.html')
    html = html\
        .replace('<!-- Add location list here -->', js_list_content)\
        .replace('{{APIToken}}', settings.google_maps_api_key)\
        .replace('{{icon_bucket}}', settings.map_icon_bucket)
    return Response(html, HTTPStatus.OK)


def return_error(message, code: HTTPStatus) -> Response:
    template = getHTMLTemplate('message.html')
    html = render_template_string(template, message=message)
    return Response(html, code)


def gcf_entry_point(request: Request) -> Response:
    settings = getConfig()
    userId = request.args.get('UserId')
    listId = request.args.get('ListId')

    if not userId and not listId:
        # creds = login()
        # service = buildService(creds)    
        # peaks = getPeaks(settings.google_script_ID, service)
        highestHundred = getUserHillList('7lGkxQywWueeFsQckAzzt9MSfNH2', 'VEpzPdBy2lO2y0fMZoSM')
        highestHundredIds = [peak.id for peak in highestHundred.hills]
        
        VLs = getUserHillList('7lGkxQywWueeFsQckAzzt9MSfNH2', 'O8BdmcLh18UskheFtb4G')
        peaks = [SheetsHill(Highest100=False, **asdict(peak)) for peak in VLs.hills]
        
        for peak in peaks:
            if peak.id in highestHundredIds:
                peak.Highest100 = True
        

    else:
        if not userId:
            return return_error('No userId provided', HTTPStatus.BAD_REQUEST)
       
        if not listId:
            return return_error('No listId provided', HTTPStatus.BAD_REQUEST)

        hillList = getUserHillList(userId, listId)
        if not hillList:
            return return_error('Invalid parameters', HTTPStatus.BAD_REQUEST)
        peaks = hillList.hills

    return serve_map(peaks, settings)
