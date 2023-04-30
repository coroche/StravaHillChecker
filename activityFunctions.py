import StravaAPI
import utm
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopy.distance

def isHillInRange(hill, start, walkLength):
    distance = geopy.distance.geodesic((hill[1], hill[2]), (start[0], start[1])).m
    return distance <= walkLength

def isHillBagged(hill, points, n):
    for point in points.transpose():
        d = geopy.distance.geodesic((hill[1], hill[2]), (point[0], point[1])).m
        if d <= 20 + 3*n:
            return True
    return False


def checkActivityForHills(activityID, plot=False, n=1):    
    stream = StravaAPI.getActivityStreams(activityID, ['latlng'])

    distIndex = next((index for (index, d) in enumerate(stream) if d["type"] == "distance"), None)
    latLngIndex = next((index for (index, d) in enumerate(stream) if d["type"] == "latlng"), None)

    streamLatLng = np.array(stream[latLngIndex]['data'])
    walkLength = stream[distIndex]['data'][-1]

    lat = streamLatLng[:,0][0::n]
    lng = streamLatLng[:,1][0::n]

    data_set = pd.read_csv('hills.csv')
    data_frames = pd.DataFrame(data_set)
    hills_array = np.array(data_frames.values)
    hills_array = np.array([hill for hill in hills_array if isHillInRange(hill, [lat[0], lng[0]], walkLength)])
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
    return old_description

def updateAllDescriptions():
    activities = StravaAPI.getLoggedInAthleteActivities()
    hikes = [activity for activity in activities if activity['sport_type']  in ['Hike', 'Walk', 'Run', 'Trail Run']]
    activityIDs = [hike['id'] for hike in hikes]

    for activityID in activityIDs:
        processActivity(activityID)

def processActivity(activityID):
    hills = checkActivityForHills(activityID, plot=False, n=10)
    if len(hills) != 0:
        custom_description = getCustomDescription(activityID)
        #print(hills, activityID)
        populateDescription(activityID, hills, custom_description = custom_description)
        return True
    else:
        return False
