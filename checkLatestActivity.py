from StravaAPI import getActivities
from activityFunctions import processActivity

latestActivityID = getActivities(1,1)[0]['id']
processActivity(latestActivityID)