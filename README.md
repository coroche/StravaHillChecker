# StravaHillChecker
This application integrates with Strava and Google Cloud APIs to keep track what Vandeleur-Lynams hills have been climbed. [See more...](https://coroche.github.io/vl/)

When an activity is uploaded to Strava, a webhook notification is received by the StravaHillChecker application running on a Raspberry Pi. A list of hills of interest (including coordinates) is retreived from a cloud hosted Google Sheets file. This is checked against the Strava activity GPX to find any hills climbed during the activity. If any are found, the spreadsheet is updated and the hill names are added to the Strava activity description.

![HillCheckerWorkflow](https://github.com/coroche/StravaHillChecker/assets/49063400/67960c10-a0bf-40bc-a7f4-53787bf6d642)
