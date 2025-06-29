from library import StravaAPI
from Tests import testdata
from data import config, userDAO
from pytest import fixture, raises
from pytest_mock import MockerFixture
from requests import Response
import json
from unittest.mock import MagicMock
from datetime import datetime, timezone, timedelta


data = testdata.getTestData()
settings = config.getConfig()
user = userDAO.getUser(userId=data.UserId)
if user.strava_token_expiry < datetime.now(timezone.utc):
    tokens = StravaAPI.getNewTokens(user)
    user.updateStravaTokens(tokens.access_token, tokens.refresh_token, tokens.expires_in)

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
    'https://www.strava.com/api/v3/oauth/token': mock_response(url='https://www.strava.com/api/v3/oauth/token', json_data={"token_type": "Bearer", "expires_at": int((datetime.now() + timedelta(hours=6)).timestamp()), "expires_in": 21600, "refresh_token": "new_refresh_token", "access_token": "new_access_token",
}),
}

def mock_request_side_effect(method, url, **kwargs):
    if kwargs.get('headers', {}).get('Authorization') == 'Bearer invalid_access_token':
        return mock_response(url=url, status_code=401, json_data={"message":"Authorization Error","errors":[{"resource":"test","field":"access_token","code":"invalid"}]})
    elif kwargs.get('data', {}).get('refresh_token') == 'invalid_refresh_token' and url == 'https://www.strava.com/api/v3/oauth/token':
        return mock_response(url=url, status_code=400, json_data={"message":"Bad Request","errors":[{"resource":"RefreshToken","field":"refresh_token","code":"invalid"}]})
    else:  
        return mock_responses.get(url, {'error': 'not found'})

@fixture
def mock_request(mocker: MockerFixture):
    mocked_request = mocker.patch('library.StravaAPI.requests.request')
    mocked_request.side_effect = mock_request_side_effect
    return mocked_request

@fixture
def mock_db(mocker: MockerFixture):
    mock_db = MagicMock()
    mocker.patch.object(userDAO, 'db', mock_db)
    mock_collection = MagicMock()
    mock_doc_ref = MagicMock()
    mock_db.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_doc_ref

    return mock_db

def test_getLoggedInAthlete(mock_request: MagicMock):
    athlete = StravaAPI.getLoggedInAthlete(user)
    assert athlete
    assert athlete.fullname == 'CormacRoche'
    assert mock_request.call_count == 1

def test_getActivities():
    activities = StravaAPI.getActivities(user, 20, 1)
    assert activities
    assert all([isinstance(activity, StravaAPI.Activity) for activity in activities])
    for activity in activities:
        for attr, value in activity.__dict__.items():
            assert value is not None, f"Attribute '{attr}' has no value in {activity}"

def test_getActivityById():
    activity = StravaAPI.getActivityById(user, data.ActivityWithHills)
    assert activity.id == data.ActivityWithHills
    for attr, value in activity.__dict__.items():
        assert value is not None, f"Attribute '{attr}' has no value in {activity}"

def test_getActivityStreams():
    streams = StravaAPI.getActivityStreams(user, data.ActivityWithHills, ['latlng'])
    assert streams
    stream = streams[0]
    assert stream.type == 'latlng'
    assert stream.data

def test_getPrimaryActivityPhoto_activityWithPhoto():
    photoUrl = StravaAPI.getPrimaryActivityPhoto(user, data.ActivityWithHills)
    assert photoUrl
    assert photoUrl != settings.default_email_image
    
def test_getPrimaryActivityPhoto_activityWithoutPhoto():
    photoUrl = StravaAPI.getPrimaryActivityPhoto(user, data.ActivityWithoutHills)
    assert photoUrl == settings.default_email_image

def test_getActivityKudoers_WithKudos():
    activity = StravaAPI.getActivityById(user, data.ActivityWithHills)
    assert activity.kudos_count != 0
    kudoers = StravaAPI.getActivityKudoers(user, activity.id, activity.kudos_count)
    assert kudoers

def test_getActivityKudoers_WithoutKudos():
    activity = StravaAPI.getActivityById(user, data.ActivityWithoutHills)
    assert activity.kudos_count == 0
    kudoers = StravaAPI.getActivityKudoers(user, activity.id, activity.kudos_count)
    assert not kudoers

def test_updateActivityDescription():
    activity = StravaAPI.getActivityById(user, data.ActivityWithHills)
    oldDescription = activity.description
    activity = StravaAPI.updateActivityDescription(user, activity.id, "This is a test")
    assert activity.description == "This is a test"
    activity = StravaAPI.updateActivityDescription(user, activity.id, oldDescription)
    assert activity.description == oldDescription

def test_getSubscriptions():
    subscriptions = StravaAPI.getSubscriptions()
    assert len(subscriptions) == 1
    assert subscriptions[0].callback_url == f'{settings.google_functions_url}/stravaWebhook'

def test_expiredToken(mock_db: MagicMock, mock_request: MagicMock):
    expiredTokenUser = userDAO.User(id='abc', email='test@mail.com', athlete_id=1, hill_lists=[], strava_access_token='old_access_token', strava_refresh_token='old_refresh_token', strava_token_expiry=datetime.now(timezone.utc) - timedelta(seconds=1))
    mock_doc_ref = mock_db.collection('users').document('abc')
    mock_doc_ref.update = MagicMock()
    
    athlete = StravaAPI.getLoggedInAthlete(expiredTokenUser)
    assert mock_request.call_count == 2 #One auth call, 1 athlete call
    assert athlete
    mock_db.collection('users').document('abc').update.assert_called_once()
    assert expiredTokenUser.strava_access_token == 'new_access_token'
    assert expiredTokenUser.strava_refresh_token == 'new_refresh_token'


def test_invalidToken(mock_db: MagicMock, mock_request: MagicMock):
    invalidTokenUser = userDAO.User(id='abc', email='test@mail.com', athlete_id=1, hill_lists=[], strava_access_token='invalid_access_token', strava_refresh_token='old_refresh_token', strava_token_expiry=datetime.now(timezone.utc) + timedelta(hours=1))
    mock_doc_ref = mock_db.collection('users').document('abc')
    mock_doc_ref.update = MagicMock()
    
    athlete = StravaAPI.getLoggedInAthlete(invalidTokenUser)
    assert mock_request.call_count == 3 #One attempted athlete call, one auth call, one successful athlete call
    assert athlete
    mock_db.collection('users').document('abc').update.assert_called_once()
    assert invalidTokenUser.strava_access_token == 'new_access_token'
    assert invalidTokenUser.strava_refresh_token == 'new_refresh_token'

def test_invalidRefreshToken(mock_db: MagicMock, mock_request: MagicMock):
    invalidTokenUser = userDAO.User(id='abc', email='test@mail.com', athlete_id=1, hill_lists=[], strava_access_token='invalid_access_token', strava_refresh_token='invalid_refresh_token', strava_token_expiry=datetime.now(timezone.utc) + timedelta(hours=1))
    mock_doc_ref = mock_db.collection('users').document('abc')
    mock_doc_ref.update = MagicMock()
    with raises(Exception) as e:
        _ = StravaAPI.getLoggedInAthlete(invalidTokenUser)
    assert str(e.value) == 'Invalid refresh token. User reauthorization required.'
    assert mock_request.call_count == 2 #One attempted athlete call, one attempted auth call
    assert mock_db.collection('users').document('abc').update.call_count == 0
    assert invalidTokenUser.strava_access_token == 'invalid_access_token'
    assert invalidTokenUser.strava_refresh_token == 'invalid_refresh_token'

def test_validToken(mock_db: MagicMock, mock_request: MagicMock):
    validTokenUser = userDAO.User(id='abc', email='test@mail.com', athlete_id=1, hill_lists=[], strava_access_token='valid_access_token', strava_refresh_token='refresh_token', strava_token_expiry=datetime.now(timezone.utc) + timedelta(hours=1))
    mock_doc_ref = mock_db.collection('users').document('abc')
    mock_doc_ref.update = MagicMock()
    
    athlete = StravaAPI.getLoggedInAthlete(validTokenUser)
    assert mock_request.call_count == 1 #One successful athlete call
    assert athlete
    assert mock_db.collection('users').document('abc').update.call_count == 0
    assert validTokenUser.strava_access_token == 'valid_access_token'
    assert validTokenUser.strava_refresh_token == 'refresh_token'

