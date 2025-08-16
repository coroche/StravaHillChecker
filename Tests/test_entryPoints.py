from flask import Flask, Request
import main_stravaWebhook
import main_processActivity
import main_subscribe
import main_getMap
import main_getChart
import main_stravaAuth
from werkzeug.test import EnvironBuilder
from data import config, userDAO
from library.googleSheetsAPI import Hill
from library.StravaAPI import Activity
from pytest import fixture
from pytest_mock import MockerFixture
from unittest.mock import MagicMock
from Tests.testdata import getTestData
from firebase_admin.auth import InvalidIdTokenError

testData = getTestData()
settings = config.getConfig()
app = Flask(__name__)


@fixture(autouse=True)
def mock_processActivity(mocker: MockerFixture) -> MagicMock:
    mocked_ProcessActivity = mocker.patch('main_processActivity.processActivity')
    hill1 = Hill(id=1, name='Hill1', latitude=0.0, longitude=0.0, done=True, Area='Area1', Highest100=True, Height=1000)
    hill2 = Hill(id=2, name='Hill2', latitude=0.0, longitude=0.0, done=True, Area='Area2', Highest100=True, Height=1000)
    hill3 = Hill(id=3, name='Hill3', latitude=0.0, longitude=0.0, done=False, Area='Area3', Highest100=False, Height=1000)
    hills = [hill1, hill2, hill3]
    mocked_ProcessActivity.side_effect = lambda activityId, _: {
            12345: (True, hills)
        }.get(activityId, None) 
    return mocked_ProcessActivity

@fixture(autouse=True)
def mock_deleteActivity(mocker: MockerFixture) -> MagicMock:
    mocked_ProcessActivity = mocker.patch('data.userDAO.User.deleteActivity')
    return mocked_ProcessActivity


@fixture(autouse=True)
def mock_getActivityByID(mocker: MockerFixture):
    mocked_GetActivity = mocker.patch('main_processActivity.getActivityById')
    mocked_GetActivity.side_effect = lambda _, activityId: {
            12345: Activity(id=12345, name='Activity1', start_date='2000-01-01T00:00:00Z', start_date_local='2000-01-01T00:00:00Z', sport_type='Hike', distance=1000, moving_time=100, total_elevation_gain=1000, visibility='everyone', private=False, kudos_count=10)
        }.get(activityId, None)
    return mocked_GetActivity


@fixture(autouse=True)
def mock_getActivities(mocker: MockerFixture):
    mocked_GetActivities = mocker.patch('main_processActivity.getActivities')
    mocked_GetActivities.return_value = [Activity(id=12345, name='Activity1', start_date='2000-01-01T00:00:00Z', start_date_local='2000-01-01T00:00:00Z', sport_type='Hike', distance=1000, moving_time=100, total_elevation_gain=1000, visibility='everyone', private=False, kudos_count=10)]
    return mocked_GetActivities


@fixture(autouse=True)
def mock_writeConfig(mocker: MockerFixture):
    mocked_WriteConfig = mocker.patch('main_processActivity.config.write')
    return mocked_WriteConfig


@fixture(autouse=True)
def mock_getConfig(mocker: MockerFixture):
    mocked_ConfigGet = mocker.patch('main_processActivity.config.get')
    mocked_ConfigGet.side_effect = lambda key: {
            'last_parsed_activity': 12344
        }.get(key, None)
    return mocked_ConfigGet


@fixture(autouse=True)
def mock_deleteRecipient(mocker: MockerFixture):
    mocked_DeleteRecipient = mocker.patch('data.config.deleteRecipient')
    return mocked_DeleteRecipient


@fixture(autouse=True, scope="function")
def mock_processActivityFromWebhookListener(mocker: MockerFixture):
    mocked_ProcessActivity = mocker.patch('main_stravaWebhook.callProcessActivity')
    return mocked_ProcessActivity

@fixture(autouse=True)
def mock_verifyIdToken(mocker: MockerFixture):
    def mock_handler(token):
        if token == "InvalidToken":
            raise InvalidIdTokenError("Token is invalid")
        return {
            'uid': testData.TestUserId,
            'email': '',
            'name': 'Test User'
        }
    mocked_verifyIdToken = mocker.patch('firebase_admin.auth.verify_id_token')
    mocked_verifyIdToken.side_effect = mock_handler
    return mocked_verifyIdToken

@fixture(autouse=True)
def mock_stravaAuthorise(mocker: MockerFixture):
    mocked_stravaAuthorise = mocker.patch('library.StravaAPI.authorise')
    mocked_stravaAuthorise.return_value = True, {
        "token_type": "Bearer",
        "expires_at": 1568775134,
        "expires_in": 21600,
        "refresh_token": "ABC123",
        "access_token": "123ABC",
        "athlete": {
            "id": 54321
        }
    }
    return mocked_stravaAuthorise


def create_sample_request(method='GET', path='/sample', data=None, params=None):
    builder = EnvironBuilder(method=method, path=path, json=data, query_string=params)
    env = builder.get_environ()
    request = Request(env)
    return request



def test_webhookListener(mock_processActivityFromWebhookListener: MagicMock):
    with app.test_request_context('/stravaWebhook'):       
        request = create_sample_request(method='POST', data={"aspect_type": "create", 'object_id':12345, 'object_type':'activity', "owner_id": 54321, "subscription_id": settings.webhook_subscription_id})
        response = main_stravaWebhook.hello_http(request, testMode=True)
        assert response == ('Processing activity 12345', 200)
        assert mock_processActivityFromWebhookListener.call_count == 1
        assert mock_processActivityFromWebhookListener.call_args.args == (12345,54321)
        mock_processActivityFromWebhookListener.reset_mock()

def test_webhookListenerInvalidSubscriptionId(mock_processActivityFromWebhookListener: MagicMock):
    with app.test_request_context('/stravaWebhook'):       
        request = create_sample_request(method='POST', data={"aspect_type": "create", 'object_id':12345, 'object_type':'activity', "owner_id": 54321, "subscription_id": settings.webhook_subscription_id + 1})
        response = main_stravaWebhook.hello_http(request, testMode=True)
        assert response == ('Invalid athleteID and subscriptionID combination', 200)
        assert mock_processActivityFromWebhookListener.call_count == 0
        mock_processActivityFromWebhookListener.reset_mock()


def test_webhookListenerPrivateActivity(mock_processActivityFromWebhookListener: MagicMock):
    with app.test_request_context('/stravaWebhook'):       
        request = create_sample_request(method='POST', data={"aspect_type": "update","object_id": 12345,"object_type": "activity","owner_id": 54321,"updates": {"private": "true"}, "subscription_id": settings.webhook_subscription_id})
        response = main_stravaWebhook.hello_http(request, testMode=True)
        assert response == ('Removing activity 12345', 200)
        assert mock_processActivityFromWebhookListener.call_count == 1
        assert mock_processActivityFromWebhookListener.call_args.args == (12345,54321)
        assert mock_processActivityFromWebhookListener.call_args.kwargs == {'deleteActivity': True}
        mock_processActivityFromWebhookListener.reset_mock()

def test_webhookListenerDeletedActivity(mock_processActivityFromWebhookListener: MagicMock):
    with app.test_request_context('/stravaWebhook'):       
        request = create_sample_request(method='POST', data={"aspect_type": "delete","object_id": 12345,"object_type": "activity","owner_id": 54321, "subscription_id": settings.webhook_subscription_id})
        response = main_stravaWebhook.hello_http(request, testMode=True)
        assert response == ('Removing activity 12345', 200)
        assert mock_processActivityFromWebhookListener.call_count == 1
        assert mock_processActivityFromWebhookListener.call_args.args == (12345,54321)
        assert mock_processActivityFromWebhookListener.call_args.kwargs == {'deleteActivity': True}
        mock_processActivityFromWebhookListener.reset_mock()


def test_webhookVerification():
    with app.test_request_context('/stravaWebhook'):
        request = create_sample_request(method='GET', params=f'hub.mode=subscribe&hub.verify_token={settings.webhook_verify_token}&hub.challenge=test_challenge')
        response, status_code = main_stravaWebhook.hello_http(request)
        assert status_code == 200
        assert response.json['hub.challenge'] == 'test_challenge'


def test_processActivity(mock_processActivity: MagicMock):
    with app.test_request_context('/processActivity'):  
        request = create_sample_request(method='POST', params=f'activityID=12345&athleteID={testData.AthleteId}')
        response, status_code = main_processActivity.hello_http(request)
    
    assert status_code == 200
    assert response.json['ActivityID'] == 12345
    assert response.json['Hills'] == [
        {'done': True, 'id': 1, 'latitude': 0.0, 'longitude': 0.0, 'name': 'Hill1', 'Area': 'Area1', 'Highest100': True, 'Height': 1000, 'ActivityID':None}, 
        {'done': True, 'id': 2, 'latitude': 0.0, 'longitude': 0.0, 'name': 'Hill2', 'Area': 'Area2', 'Highest100': True, 'Height': 1000, 'ActivityID':None},
        {'done': False, 'id': 3, 'latitude': 0.0, 'longitude': 0.0, 'name': 'Hill3', 'Area': 'Area3', 'Highest100': False, 'Height': 1000, 'ActivityID':None}
    ]
    assert response.json['HillsClimbed'] == 3
    assert mock_processActivity.call_count == 1

    user = userDAO.getUser(userId=testData.UserId)
    assert mock_processActivity.call_args.args == (12345, user)


def test_DeleteActivity(mock_deleteActivity: MagicMock):
    with app.test_request_context('/processActivity'):  
        request = create_sample_request(method='POST', params=f'activityID=12345&athleteID={testData.AthleteId}&deleteActivity=true')
        response, status_code = main_processActivity.hello_http(request)
    
    assert status_code == 200
    assert response.json['ActivityID'] == 12345
    assert response.json['message'] == 'Activity removed from completed hills list'
    assert mock_deleteActivity.call_count == 1
    assert mock_deleteActivity.call_args.args == (12345,)


def test_processLatestActivity(mock_processActivity: MagicMock, mock_writeConfig: MagicMock):
    with app.test_request_context('/processActivity'):  
        request = create_sample_request(method='POST', params=f'activityID=0&athleteID={testData.AthleteId}')
        response, status_code = main_processActivity.hello_http(request)
    
    assert status_code == 200
    assert response.json['ActivityID'] == 12345
    assert response.json['Hills'] == [
        {'done': True, 'id': 1, 'latitude': 0.0, 'longitude': 0.0, 'name': 'Hill1', 'Area': 'Area1', 'Highest100': True, 'Height': 1000, 'ActivityID':None}, 
        {'done': True, 'id': 2, 'latitude': 0.0, 'longitude': 0.0, 'name': 'Hill2', 'Area': 'Area2', 'Highest100': True, 'Height': 1000, 'ActivityID':None},
        {'done': False, 'id': 3, 'latitude': 0.0, 'longitude': 0.0, 'name': 'Hill3', 'Area': 'Area3', 'Highest100': False, 'Height': 1000, 'ActivityID':None}
    ]    
    assert response.json['HillsClimbed'] == 3
    assert mock_processActivity.call_count == 1

    user = userDAO.getUser(userId=testData.UserId)
    assert mock_processActivity.call_args.args == (12345, user)

    assert mock_writeConfig.call_count == 1
    assert mock_writeConfig.call_args.args == ('last_parsed_activity', 12345)


def test_unsubscribe(mock_deleteRecipient: MagicMock):
    with app.test_request_context('/subscribe/unsubscribe'):
        
        request = create_sample_request(method='GET', path = '/unsubscribe', params= 'subscriberID=123ABC')
        response = main_subscribe.gcf_entry_point(request)

        assert 'You have been unsubscribed and we are no longer friends.' in response.get_data(as_text=True)
        assert response.status_code == 200
        assert mock_deleteRecipient.call_count == 1
        assert mock_deleteRecipient.call_args.args == ('123ABC',)

def test_getMap():
    with app.test_request_context('/getMap'):
        request = create_sample_request(params= f'UserId={testData.UserId}&ListId={testData.HillListID}')
        response = main_getMap.gcf_entry_point(request)
        assert response
        assert response.status_code == 200
        assert '"PeakDoneIcon"' in str(response.data) or '"PeakIcon"' in str(response.data)

def test_getDefaultMap():
    with app.test_request_context('/getMap'):
        request = create_sample_request()
        response = main_getMap.gcf_entry_point(request)
        assert response
        assert response.status_code == 200
        assert '"VLDoneIcon"' in str(response.data) or '"VLIcon"' in str(response.data)

def test_getInvalidMap():
    with app.test_request_context('/getMap'):
        request = create_sample_request(params= f'UserId={testData.UserId}&ListId={testData.HillListID}X')
        response = main_getMap.gcf_entry_point(request)
        assert response
        assert response.status_code == 400
        assert 'Invalid parameters' in str(response.data)

def test_getChart():
    with app.test_request_context('/getChart'):
        request = create_sample_request(params= f'UserId={testData.UserId}&ListId={testData.HillListID}')
        response = main_getChart.gcf_entry_point(request)
        assert response
        assert response.status_code == 200

def test_stravaAuth():
    with app.test_request_context('/stravaAuth'):
        request = create_sample_request(params='code=myCode&state=ValidToken&scope=read,write')
        response = main_stravaAuth.gcf_entry_point(request)
        assert response
        assert response.status_code == 200
        assert 'Strava connected successfully!' in str(response.data)

def test_stravaAuth_UserDoesntExist():
    with app.test_request_context('/stravaAuth'):
        request = create_sample_request(params='code=myCode&state=InvalidToken&scope=read,write')
        response = main_stravaAuth.gcf_entry_point(request)
        assert response
        assert response.status_code == 401
        assert 'link denied' in str(response.data)

def test_stravaAuth_Error():
    with app.test_request_context('/stravaAuth'):
        request = create_sample_request(params='code=myCode&state=ValidToken&scope=read,write&error=access_denied')
        response = main_stravaAuth.gcf_entry_point(request)
        assert response
        assert response.status_code == 401
        assert 'link denied' in str(response.data)



