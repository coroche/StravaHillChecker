from library.StravaAPI import getActivities
from library.activityFunctions import processActivity
from data import config

def main():
    latestActivityID = getActivities(1,1)[0].id
    lastParsedActivity = config.get('last_parsed_activity')

    if latestActivityID != lastParsedActivity:
        processActivity(latestActivityID)
        config.write('last_parsed_activity', latestActivityID)

if __name__ == "__main__":
    main()