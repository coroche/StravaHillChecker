# StravaHillChecker
This application integrates with Strava and Google Cloud APIs to keep track what Vandeleur-Lynams hills have been climbed. [See more...](https://coroche.github.io/vl/)

When an activity is uploaded to Strava, a webhook notification is received by a Google Cloud Function. A list of hills of interest (including coordinates) is retreived from a Firestore database. This is checked against the Strava activity GPX to find any hills climbed during the activity. If any are found, the database is updated and the hill names are added to the Strava activity description.

![HillCheckerWorkflow](https://github.com/coroche/StravaHillChecker/assets/49063400/e0f4c1ca-f1a5-4e56-a531-7f4e187179f8)
