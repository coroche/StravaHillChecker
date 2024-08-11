from flask import Flask, Request
import main_stravaWebhook
import main_processActivity
import main_processLatestActivity
import main_subscribe
from werkzeug.test import EnvironBuilder
from data import config
from library.googleSheetsAPI import Hill
from library.StravaAPI import Activity

app = Flask(__name__)
settings = config.getConfig()


def create_sample_request(method='GET', path='/sample', data=None, params=None):
    # Construct an environment for the request
    builder = EnvironBuilder(method=method, path=path, json=data, query_string=params)
    env = builder.get_environ()

    # Create a Request object using the constructed environment
    request = Request(env)
    return request

def test_webhookListener(mocker):
    with app.test_request_context('/stravaWebhook'):
        #Mock call to prevent activity processing
        mocked_ProcessActivity = mocker.patch('main_stravaWebhook.callProcessActivity')
        
        request = create_sample_request(method='POST', data={'object_type':'activity', 'object_id':12345})
        response = main_stravaWebhook.hello_http(request)
        assert response == ('Processing activity 12345', 200)
        assert mocked_ProcessActivity.call_count == 1
        assert mocked_ProcessActivity.call_args.args == (12345,)


def test_webhookVerification():
    with app.test_request_context('/stravaWebhook'):
        request = create_sample_request(method='GET', params=f'hub.mode=subscribe&hub.verify_token={settings.webhook_verify_token}&hub.challenge=test_challenge')
        response, status_code = main_stravaWebhook.hello_http(request)
        assert status_code == 200
        assert response.json['hub.challenge'] == 'test_challenge'

def test_processActivity(mocker):

    #Mock call to prevent activity processing
    mocked_ProcessActivity = mocker.patch('main_processActivity.processActivity')
    hill1 = Hill(1, 'Hill1', 0.0, 0.0, True, 'Area1', True, 1000)
    hill2 = Hill(2, 'Hill2', 0.0, 0.0, True, 'Area2', True, 1000)
    hill3 = Hill(3, 'Hill3', 0.0, 0.0, False, 'Area3', False, 1000)
    hills = [hill1, hill2, hill3]
    mocked_ProcessActivity.return_value = (None, hills)
    
    mocked_GetActivity = mocker.patch('main_processActivity.getActivityById')
    mocked_GetActivity.return_value = Activity(12345, 'Activity1', '2000-01-01T00:00:00Z', '2000-01-01T00:00:00Z', 'Hike', 1000, 100, 1000, 'everyone', False, 10)
    
    with app.test_request_context('/processActivity'):  
        request = create_sample_request(method='POST', params='activityID=12345')
        response, status_code = main_processActivity.hello_http(request)
    
    assert status_code == 200
    assert response.json['ActivityID'] == 12345
    assert response.json['Hills'] == [
        {'done': True, 'id': 1, 'latitude': 0.0, 'longitude': 0.0, 'name': 'Hill1', 'Area': 'Area1', 'Highest100': True, 'Height': 1000, 'ActivityID':None}, 
        {'done': True, 'id': 2, 'latitude': 0.0, 'longitude': 0.0, 'name': 'Hill2', 'Area': 'Area2', 'Highest100': True, 'Height': 1000, 'ActivityID':None},
        {'done': False, 'id': 3, 'latitude': 0.0, 'longitude': 0.0, 'name': 'Hill3', 'Area': 'Area3', 'Highest100': False, 'Height': 1000, 'ActivityID':None}
    ]
    assert response.json['HillsClimbed'] == 3
    assert mocked_ProcessActivity.call_count == 1
    assert mocked_ProcessActivity.call_args.args == (12345,)


def test_processLatestActivity(mocker):

    #Mock call to prevent activity processing
    mocked_ProcessActivity = mocker.patch('main_processLatestActivity.processActivity')
    hill1 = Hill(1, 'Hill1', 0.0, 0.0, True, 'Area1', True, 1000)
    hill2 = Hill(2, 'Hill2', 0.0, 0.0, True, 'Area2', True, 1000)
    hill3 = Hill(3, 'Hill3', 0.0, 0.0, False, 'Area3', False, 1000)
    hills = [hill1, hill2, hill3]
    mocked_ProcessActivity.return_value = (None, hills)
    
    mocked_GetActivity = mocker.patch('main_processLatestActivity.getActivities')
    mocked_GetActivity.return_value = [Activity(12345, 'Activity1', '2000-01-01T00:00:00Z', '2000-01-01T00:00:00Z', 'Hike', 1000, 100, 1000, 'everyone', False, 10)]
    
    mocked_WriteConfig = mocker.patch('main_processLatestActivity.config.write')


    with app.test_request_context('/processActivity'):  
        request = create_sample_request(method='POST', params='activityID=12345')
        response, status_code = main_processLatestActivity.hello_http(request)
    
    assert status_code == 200
    assert response.json['ActivityID'] == 12345
    assert response.json['Hills'] == [
        {'done': True, 'id': 1, 'latitude': 0.0, 'longitude': 0.0, 'name': 'Hill1', 'Area': 'Area1', 'Highest100': True, 'Height': 1000, 'ActivityID':None}, 
        {'done': True, 'id': 2, 'latitude': 0.0, 'longitude': 0.0, 'name': 'Hill2', 'Area': 'Area2', 'Highest100': True, 'Height': 1000, 'ActivityID':None},
        {'done': False, 'id': 3, 'latitude': 0.0, 'longitude': 0.0, 'name': 'Hill3', 'Area': 'Area3', 'Highest100': False, 'Height': 1000, 'ActivityID':None}
    ]    
    assert response.json['HillsClimbed'] == 3
    assert mocked_ProcessActivity.call_count == 1
    assert mocked_ProcessActivity.call_args.args == (12345,)
    assert mocked_WriteConfig.call_count == 1
    assert mocked_WriteConfig.call_args.args == ('last_parsed_activity', 12345)

def test_unsubscribe(mocker):
    with app.test_request_context('/subscribe/unsubscribe'):
        #Mock call to prevent activity processing
        mocked_DeleteRecipient = mocker.patch('data.config.deleteRecipient')
        
        request = create_sample_request(method='GET', path = '/unsubscribe', params= 'subscriberID=123ABC')
        response = main_subscribe.gcf_entry_point(request)

        assert 'You have been unsubscribed and we are no longer friends.' in response.get_data(as_text=True)
        assert response.status_code == 200
        assert mocked_DeleteRecipient.call_count == 1
        assert mocked_DeleteRecipient.call_args.args == ('123ABC',)
