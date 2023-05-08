import StravaAPI
import googleSheetsAPI
import utm
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime


def isHillBagged(hill, points, n):
    lat_diffs = np.abs(points[0] - hill[1])
    lon_diffs = np.abs(points[1] - hill[2])

    matches = np.logical_or(lat_diffs <= 0.0002*n, lon_diffs <= 0.0003*n)
    return matches.any()


def checkActivityForHills(activityID, plot=False, n=1):    
    stream = StravaAPI.getActivityStreams(activityID, ['latlng'])

    latLngIndex = next((index for (index, d) in enumerate(stream) if d["type"] == "latlng"), None)
    streamLatLng = np.array(stream[latLngIndex]['data'])
    lat = streamLatLng[:,0][0::n]
    lng = streamLatLng[:,1][0::n]

    data_set = pd.read_csv('hills.csv')
    data_frames = pd.DataFrame(data_set)
    hills_array = np.array(data_frames.values)
    hills_array = np.array([hill for hill in hills_array if isHillBagged(hill, np.array([lat, lng]), n)])

    if plot:
        route_cartesian = utm.from_latlon(lat,lng)
        minX = min(route_cartesian[0])
        minY = min(route_cartesian[1])
        x = [i - minX for i in route_cartesian[0]]
        y = [i - minY for i in route_cartesian[1]]
        plt.plot(x, y, 'r-')

        if hills_array.size != 0:

            hills_lat = np.array(hills_array[:,1]).astype(float)
            hills_lng = np.array(hills_array[:,2]).astype(float)

            hills_cartesian = utm.from_latlon(hills_lat,hills_lng)
            hills_cartesian_x = [i - minX for i in hills_cartesian[0]]
            hills_cartesian_y = [i - minY for i in hills_cartesian[1]]

            plt.plot(hills_cartesian_x, hills_cartesian_y, 'o')

        ax = plt.gca()
        ax.set_aspect('equal', adjustable='box')
        plt.show()

    if hills_array.size != 0:
        return hills_array[:,0]
    else:
        return []


def populateDescription(activityID, hills, custom_description = ""):
        hills = ['✅ ' + hill for hill in hills]
        description = '\n'.join(hills)
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

def updateSpreadsheet(hills, activityDate):
    SCRIPT_ID = googleSheetsAPI.getScriptID()
    creds = googleSheetsAPI.login()
    service = googleSheetsAPI.buildService(creds)

    googleSheetsAPI.markAsDoneByNames(SCRIPT_ID, service, hills, activityDate)

def processActivity(activityID):
    hills = checkActivityForHills(activityID, plot=False, n=10)
    if len(hills) != 0:
        custom_description, activityDate = getCustomDescription(activityID)
        populateDescription(activityID, hills, custom_description = custom_description)
        updateSpreadsheet(hills.tolist(), activityDate)
        return True
    else:
        return False
