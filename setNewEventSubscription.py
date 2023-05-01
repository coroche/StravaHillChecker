import StravaAPI

def setNewEventSubscription():
    subs = StravaAPI.getSubscriptions()
    for sub in subs:
        StravaAPI.deleteSubscription(sub['id'])
    StravaAPI.createSubscription()

if __name__ == "__main__":
    setNewEventSubscription()