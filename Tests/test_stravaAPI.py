from  library import StravaAPI
from Tests import testdata
from data import config

data = testdata.getTestData()
settings = config.getConfig()

def test_getLoggedInAthlete():
    athlete = StravaAPI.getLoggedInAthlete()
    assert athlete
    assert athlete.fullname == 'CormacRoche'

def test_getActivities():
    activities = StravaAPI.getActivities(20, 1)
    assert activities
    assert all([isinstance(activity, StravaAPI.Activity) for activity in activities])
    for activity in activities:
        for attr, value in activity.__dict__.items():
            assert value is not None, f"Attribute '{attr}' has no value in {activity}"

def test_getActivityById():
    activity = StravaAPI.getActivityById(data.ActivityWithHills)
    assert activity.id == data.ActivityWithHills
    for attr, value in activity.__dict__.items():
        assert value is not None, f"Attribute '{attr}' has no value in {activity}"

def test_getActivityStreams():
    streams = StravaAPI.getActivityStreams(data.ActivityWithHills, ['latlng'])
    assert streams
    stream = streams[0]
    assert stream.type == 'latlng'
    assert stream.data

def test_getPrimaryActivityPhoto_activityWithPhoto():
    photoUrl = StravaAPI.getPrimaryActivityPhoto(data.ActivityWithHills)
    assert photoUrl
    assert photoUrl != settings.default_email_image
    
def test_getPrimaryActivityPhoto_activityWithoutPhoto():
    photoUrl = StravaAPI.getPrimaryActivityPhoto(data.ActivityWithoutHills)
    assert photoUrl == settings.default_email_image

def test_getActivityKudoers_WithKudos():
    activity = StravaAPI.getActivityById(data.ActivityWithHills)
    assert activity.kudos_count != 0
    kudoers = StravaAPI.getActivityKudoers(activity.id, activity.kudos_count)
    assert kudoers

def test_getActivityKudoers_WithoutKudos():
    activity = StravaAPI.getActivityById(data.ActivityWithoutHills)
    assert activity.kudos_count == 0
    kudoers = StravaAPI.getActivityKudoers(activity.id, activity.kudos_count)
    assert not kudoers

def test_updateActivityDescription():
    activity = StravaAPI.getActivityById(data.ActivityWithHills)
    oldDescription = activity.description
    activity = StravaAPI.updateActivityDescription(activity.id, "This is a test")
    assert activity.description == "This is a test"
    activity = StravaAPI.updateActivityDescription(activity.id, oldDescription)
    assert activity.description == oldDescription

def test_getSubscriptions():
    subscriptions = StravaAPI.getSubscriptions()
    assert len(subscriptions) == 1
    assert subscriptions[0].callback_url == f'{settings.google_functions_url}/stravaWebhook'
