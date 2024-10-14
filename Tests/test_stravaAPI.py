from library import StravaAPI
from Tests import testdata
from data import config
from pytest import fixture
from pytest_mock import MockerFixture
from requests import Response
import json

data = testdata.getTestData()
settings = config.getConfig()

def mock_response(url, status_code=200, content=None, json_data=None):
    response = Response()
    response.status_code = status_code
    response.url = url
    if json_data is not None:
        response._content = json.dumps(json_data).encode('utf-8')
    elif content is not None:
        response._content = content.encode('utf-8')
    return response


mock_responses = {
    'https://www.strava.com/api/v3/athlete': mock_response(url='https://www.strava.com/api/v3/athlete', json_data={"id":43044719,"username":None,"firstname":"Cormac","lastname":"Roche"}),
    'https://example.com/api/resource2': {'data': 'response for resource2'},
}

def mock_request_side_effect(method, url, **kwargs):
    return mock_responses.get(url, {'error': 'not found'})

@fixture
def mock_request(mocker: MockerFixture):
    mocked_request = mocker.patch('library.StravaAPI.requests.request')
    mocked_request.side_effect = mock_request_side_effect
    return mocked_request

def test_getLoggedInAthlete(mock_request):
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
