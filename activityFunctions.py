import StravaAPI
import googleSheetsAPI
import utm
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime


def isHillBagged(hill, points, n):
    lat_diffs = np.abs(points[0] - hill['Latitude'])
    lon_diffs = np.abs(points[1] - hill['Longitude'])

    matches = np.logical_or(lat_diffs <= 0.0002*n, lon_diffs <= 0.0003*n)
    return matches.any()


def checkActivityForHills(activityID, SCRIPT_ID, service, plot=False, n=1):    
    stream = StravaAPI.getActivityStreams(activityID, ['latlng'])

    latLngIndex = next((index for (index, d) in enumerate(stream) if d["type"] == "latlng"), None)
    streamLatLng = np.array(stream[latLngIndex]['data'])
    lat = streamLatLng[:,0][0::n]
    lng = streamLatLng[:,1][0::n]

    hills = googleSheetsAPI.getPeaks(SCRIPT_ID, service)
    hills = np.array([hill for hill in hills if isHillBagged(hill, np.array([lat, lng]), n)])

    if plot:
        route_cartesian = utm.from_latlon(lat,lng)
        minX = min(route_cartesian[0])
        minY = min(route_cartesian[1])
        x = [i - minX for i in route_cartesian[0]]
        y = [i - minY for i in route_cartesian[1]]
        plt.plot(x, y, 'r-')

        if hills.size != 0:

            hills_lat = np.array([hill['Latitude'] for hill in hills]).astype(float)
            hills_lng = np.array([hill['Longitude'] for hill in hills]).astype(float)

            hills_cartesian = utm.from_latlon(hills_lat,hills_lng)
            hills_cartesian_x = [i - minX for i in hills_cartesian[0]]
            hills_cartesian_y = [i - minY for i in hills_cartesian[1]]

            plt.plot(hills_cartesian_x, hills_cartesian_y, 'o')

        ax = plt.gca()
        ax.set_aspect('equal', adjustable='box')
        plt.show()

    return hills



def populateDescription(activityID, hills, custom_description = ""):
        hillNames = ['✅ ' + hill['Summit or Place'] for hill in hills]
        description = '\n'.join(hillNames)
        description = custom_description + 'VLs:\n' + description
        
        StravaAPI.updateActivityDescription(activityID, description)

def getCustomDescription(activityID):
    activity = StravaAPI.getActivityById(activityID)
    old_description = activity['description']
    if old_description != "" and 'VLs:' in old_description:
        old_description = old_description[0:old_description.find('VLs:')]
    activityDate = datetime.strptime(activity['start_date_local'], '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d')
    return old_description, activityDate

def updateAllDescriptions():
    activities = StravaAPI.getLoggedInAthleteActivities()
    hikes = [activity for activity in activities if activity['sport_type']  in ['Hike', 'Walk', 'Run', 'Trail Run']]
    activityIDs = [hike['id'] for hike in hikes]

    for activityID in activityIDs:
        processActivity(activityID)


def processActivity(activityID):
    SCRIPT_ID = googleSheetsAPI.getScriptID()
    creds = googleSheetsAPI.login()
    service = googleSheetsAPI.buildService(creds)

    hills = checkActivityForHills(activityID, SCRIPT_ID, service, plot=False, n=1)
    if len(hills) != 0:
        custom_description, activityDate = getCustomDescription(activityID)
        populateDescription(activityID, hills, custom_description = custom_description)

        hillIDs = [hill['#'] for hill in hills]
        googleSheetsAPI.markAsDone(SCRIPT_ID, service, hillIDs, activityDate)
        return True
    else:
        return False
