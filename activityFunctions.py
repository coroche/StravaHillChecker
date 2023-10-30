import StravaAPI
import googleSheetsAPI
import utm
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import config
from typing import List

settings = config.getConfig()

def isHillBagged(hill: googleSheetsAPI.Hill, points: np.ndarray, n: int) -> bool:
    lat_diffs = np.abs(points[0] - hill.latitude)
    lon_diffs = np.abs(points[1] - hill.longitude)

    matches: np.ndarray = np.logical_and(lat_diffs <= 0.0002*n, lon_diffs <= 0.0003*n)
    return matches.any()


def checkActivityForHills(activityID: int, SCRIPT_ID: str, service: googleSheetsAPI.Resource, plot: bool = False, n: int = 1) -> List[googleSheetsAPI.Hill]:    
    stream = StravaAPI.getActivityStreams(activityID, ['latlng'])[0]
    streamLatLng = np.array(stream.data)
    lat = streamLatLng[:,0][0::n]
    lng = streamLatLng[:,1][0::n]

    hills = googleSheetsAPI.getPeaks(SCRIPT_ID, service)
    hills = [hill for hill in hills if isHillBagged(hill, np.array([lat, lng]), n)]

    if plot:
        route_cartesian = utm.from_latlon(lat,lng)
        minX = min(route_cartesian[0])
        minY = min(route_cartesian[1])
        x = [i - minX for i in route_cartesian[0]]
        y = [i - minY for i in route_cartesian[1]]
        plt.plot(x, y, 'r-')

        if len(hills) != 0:

            hills_lat = np.array([hill.latitude for hill in hills]).astype(float)
            hills_lng = np.array([hill.longitude for hill in hills]).astype(float)

            hills_cartesian = utm.from_latlon(hills_lat,hills_lng)
            hills_cartesian_x = [i - minX for i in hills_cartesian[0]]
            hills_cartesian_y = [i - minY for i in hills_cartesian[1]]

            plt.plot(hills_cartesian_x, hills_cartesian_y, 'o')

        ax: plt.Axes = plt.gca()
        ax.set_aspect('equal', adjustable='box')
        plt.show()

    return hills



def populateDescription(activityID: int, hills: List[googleSheetsAPI.Hill], custom_description: str = ""):
        hillNames = ['✅ ' + hill.name for hill in hills]
        description = '\n'.join(hillNames)
        description = custom_description + 'VLs:\n' + description
        
        StravaAPI.updateActivityDescription(activityID, description)

def getActivityDetails(activityID: int) -> tuple[str, datetime]:
    activity = StravaAPI.getActivityById(activityID)
    old_description = activity.description
    if old_description is None:
        old_description = ""
    if old_description != "" and 'VLs:' in old_description:
        old_description = old_description[0:old_description.find('VLs:')]
    activityDate = datetime.strptime(activity.start_date_local, '%Y-%m-%dT%H:%M:%S%z')
    return old_description, activityDate

def updateAllDescriptions():
    activities = StravaAPI.getLoggedInAthleteActivities()
    hikes = [activity for activity in activities if activity.sport_type  in ['Hike', 'Walk', 'Run', 'Trail Run']]
    activityIDs = [hike.id for hike in hikes]

    for activityID in activityIDs:
        processActivity(activityID)


def processActivity(activityID: int) -> bool:
    creds = googleSheetsAPI.login()
    service = googleSheetsAPI.buildService(creds)

    hills = checkActivityForHills(activityID, settings.google_script_ID, service, plot=False, n=1)
    if len(hills) != 0:
        custom_description, activityDate = getActivityDetails(activityID)
        populateDescription(activityID, hills, custom_description = custom_description)

        hillIDs = [hill.id for hill in hills]
        googleSheetsAPI.markAsDone(settings.google_script_ID, service, hillIDs, activityDate, activityID)
        return True
    else:
        return False

