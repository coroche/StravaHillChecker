from library import StravaAPI
from library import googleSheetsAPI
import utm
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timezone
from data import config
from typing import List, Dict
from library.smtp import sendEmail

settings = config.getConfig()

def isHillBagged(hill: googleSheetsAPI.Hill, points: np.ndarray, n: int) -> bool:
    lat_diffs = np.abs(points[0] - hill.latitude)
    lon_diffs = np.abs(points[1] - hill.longitude)

    matches: np.ndarray = np.logical_and(lat_diffs <= 0.0002*n, lon_diffs <= 0.0003*n)
    return matches.any()


def checkActivityForHills(activityID: int, SCRIPT_ID: str, service: googleSheetsAPI.Resource, plot: bool = False, n: int = 1) -> tuple[List[googleSheetsAPI.Hill], List[googleSheetsAPI.Hill]]:    
    stream = StravaAPI.getActivityStreams(activityID, ['latlng'])[0]
    streamLatLng = np.array(stream.data)
    lat = streamLatLng[:,0][0::n]
    lng = streamLatLng[:,1][0::n]

    allHills = googleSheetsAPI.getPeaks(SCRIPT_ID, service)
    hills = [hill for hill in allHills if isHillBagged(hill, np.array([lat, lng]), n)]

    if plot:
        route_cartesian = utm.from_latlon(lat,lng)
        minX = min(route_cartesian[0])
        minY = min(route_cartesian[1])
        x = [i - minX for i in route_cartesian[0]]
        y = [i - minY for i in route_cartesian[1]]
        plt.plot(x, y, 'r-')

        if hills:

            hills_lat = np.array([hill.latitude for hill in hills]).astype(float)
            hills_lng = np.array([hill.longitude for hill in hills]).astype(float)

            hills_cartesian = utm.from_latlon(hills_lat,hills_lng)
            hills_cartesian_x = [i - minX for i in hills_cartesian[0]]
            hills_cartesian_y = [i - minY for i in hills_cartesian[1]]

            plt.plot(hills_cartesian_x, hills_cartesian_y, 'o')

        ax: plt.Axes = plt.gca()
        ax.set_aspect('equal', adjustable='box')
        plt.show()

    return hills, allHills



def populateDescription(activityID: int, hills: List[googleSheetsAPI.Hill], custom_description: str = ""):
        hillNames = ['✅ ' + hill.name for hill in hills]
        description = '\n'.join(hillNames)
        description = custom_description + 'VLs:\n' + description
        
        StravaAPI.updateActivityDescription(activityID, description)

def updateAllDescriptions():
    activities = StravaAPI.getActivities(20, 1)
    hikes = [activity for activity in activities if activity.sport_type  in ['Hike', 'Walk', 'Run', 'Trail Run']]
    activityIDs = [hike.id for hike in hikes]

    for activityID in activityIDs:
        processActivity(activityID)


def processActivity(activityID: int) -> tuple[bool, List[googleSheetsAPI.Hill]]:
    creds = googleSheetsAPI.login()
    service = googleSheetsAPI.buildService(creds)

    activityHills, allHills = checkActivityForHills(activityID, settings.google_script_ID, service, plot=False, n=1)
    

    if activityHills:
        activity = StravaAPI.getActivityById(activityID)
        populateDescription(activityID, activityHills, custom_description = activity.custom_description)

        hillIDs = [hill.id for hill in activityHills]
        googleSheetsAPI.markAsDone(settings.google_script_ID, service, hillIDs, activity.activity_date_local, activity.id)

        timeDiff = datetime.now(timezone.utc) - activity.activity_date_utc
        print(f'ActivityDate: {activity.activity_date_utc}')
        print(f'Now: {datetime.now(timezone.utc)}')
        print(f'TimeDiff: {timeDiff}')
        print(f'Private: {activity.private}')
        print(f'Less than 7 days: {timeDiff.days <= 7}')
        if not activity.private and timeDiff.days <= 7:
            notifications = config.getActivityNotifications(activity.id)
            mailingList = config.getMailingList()
            html_content = config.getHTMLTemplate('Email.html')
            html_content = composeMail(html_content, activity, activityHills, allHills)
            
            for recipient in mailingList:
                recipientNotifications = [notification for notification in notifications if notification.recipient_id == recipient.id]
                
                #If the recipient has not already been notified
                if not recipientNotifications:
                    unsubscribeLink = f'{settings.webhook_callback_url}/subscribe/unsubscribe?subscriberID={recipient.id}'
                    sendEmail(html_content.replace('{UnsubscribeLink}', unsubscribeLink), recipient.email, "Your kudos are required")
                    config.writeNotification(activity.id, recipient.id)

        return True, activityHills
    else:
        return False, activityHills

   
def composeMail(html_content: str, activity: StravaAPI.Activity, activityHills: List[googleSheetsAPI.Hill], allHills: List[googleSheetsAPI.Hill]) -> str:
    
    backgroundImg = StravaAPI.getPrimaryActivityPhoto(activity.id)

    done = len([hill for hill in allHills if hill.done])
    togo = len([hill for hill in allHills if not hill.done])
    m, _ = divmod(activity.moving_time, 60)
    h, m = divmod(m, 60)
    html_hillNames = "".join(["<li style=""margin-bottom: 0; text-align: left;"">" + hill.name + "</li>" for hill in activityHills])

    html_content = html_content\
        .replace("{Done}", f"{done}")\
        .replace("{ToGo}", f"{togo}")\
        .replace("{ActivityDistance}", f"{activity.distance/1000:.1f}km")\
        .replace("{ActivityDuration}", f'{h:d}h {m:02d}m')\
        .replace("{Hills}", html_hillNames)\
        .replace("{StravaLink}", f"https://www.strava.com/activities/{activity.id}")\
        .replace("{BackgroundImage}", backgroundImg)
    
    return html_content


def composeFollowupEmail(html_content: str, activityID: int) -> str:
    
    html_content = html_content\
        .replace("{StravaLink}", f"https://www.strava.com/activities/{activityID}")
    
    return html_content


def bullyRecipients():
    notifications = config.getUnkudosedNotifications()
    grouped_by_activity: Dict[int, List[config.Notification]] = {}
    for notification in notifications:
        if notification.activity_id not in grouped_by_activity:
            grouped_by_activity[notification.activity_id] = []
        grouped_by_activity[notification.activity_id].append(notification)
    
    for activityID, notifications in grouped_by_activity.items():
        activity = StravaAPI.getActivityById(activityID)
        if not activity.private:
            kudoers = StravaAPI.getActivityKudoers(activityID, activity.kudos_count)
            html_content = config.getHTMLTemplate('FollowUpEmail.html')
            html_content = composeFollowupEmail(html_content, activityID)
            for notification in notifications:
                recipient = config.getRecipient(notification.recipient_id)
                if recipient.on_strava:
                    if recipient.strava_fullname in [kudoer.fullname for kudoer in kudoers]:
                        config.updateNotification(activity.id, recipient.id)
                    else:
                        unsubscribeLink = f'{settings.webhook_callback_url}/subscribe/unsubscribe?subscriberID={recipient.id}'
                        sendEmail(html_content.replace('{UnsubscribeLink}', unsubscribeLink), recipient.email, 'I am once again asking for you to...')
        