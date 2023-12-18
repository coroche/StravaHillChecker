import requests
import json
import config
from typing import List
from dataclasses import dataclass

@dataclass
class Activity:
    id: int
    name: str
    description: str
    start_date_local: str
    sport_type: str
    distance: float
    moving_time: float
    total_elevation_gain: float
    visibility: str
    private: bool


@dataclass
class Athlete:  
    id: int
    firstname: str
    lastname: str


@dataclass
class Stream:
    type: str
    data: List[List[float]]


@dataclass
class Subscription:
    id: int


@dataclass
class TokenResponse:
    access_token: str
    refresh_token: str


settings = config.getConfig()

def trimData(json_data: dict, dClass: type) -> dict:
    return {key: value for key, value in json_data.items() if key in dClass.__annotations__}

def makeRequest(method: str, url: str, **kwargs) -> requests.Response:
    response = requests.request(method, url, **kwargs)
    if response.status_code == 401:
        refreshTokens()
        kwargs['headers']['Authorization'] = 'Bearer ' + settings.access_token
        response = requests.request(method, url, **kwargs)
    return response


def writeTokens():
    config.write('access_token', settings.access_token)
    config.write('refresh_token', settings.refresh_token)


def refreshTokens():
    url = settings.base_url + "/oauth/token"

    payload={
        'client_id': settings.client_id,
        'client_secret': settings.client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': settings.refresh_token
    }

    response = requests.request("POST", url, data=payload)
    token_data = trimData(json.loads(response.text), TokenResponse)
    tokens = TokenResponse(**token_data)
    
    settings.access_token = tokens.access_token
    settings.refresh_token = tokens.refresh_token

    writeTokens()


def getLoggedInAthlete() -> Athlete:
    url = settings.base_url + "/athlete"
    headers = {'Authorization': 'Bearer ' + settings.access_token}

    response = makeRequest("GET", url, headers=headers)
    athlete_data: dict = json.loads(response.text)
    athlete_data = trimData(athlete_data, Athlete)
    return Athlete(**athlete_data)


def getLoggedInAthleteActivities() -> List[Activity]:
    url = settings.base_url + "/athlete/activities"
    headers = {'Authorization': 'Bearer ' + settings.access_token}
    params = {
        'per_page': 20,
        'page': 1
    }

    response = makeRequest("GET", url, headers=headers, params=params)
    activity_list = []
    for activity_data in json.loads(response):
        activity_list.append(Activity(activity_data))
    return activity_list


def getActivityById(activityID: int) -> Activity:
    url = settings.base_url + "/activities/" + str(activityID)
    headers = {'Authorization': 'Bearer ' + settings.access_token}

    response = makeRequest("GET", url, headers=headers)
    if response.status_code == 404:
        return Activity(0, '','','','')
    activity_json: dict = json.loads(response.text)
    activity_json = trimData(activity_json, Activity)
    activity = Activity(**activity_json)
    return activity


def getActivityStreams(activityID: int, streamTypes: List[str]) -> List[Stream]:
    url = settings.base_url + "/activities/" + str(activityID) + "/streams"
    streamTypes_str = str(streamTypes).replace("'","").replace(" ","")[1:-1]
    
    headers = {'Authorization': 'Bearer ' + settings.access_token}
    params = {'keys': streamTypes_str}

    response = makeRequest("GET", url, headers=headers, params=params)  
    streams_list: List[Stream] = []
    for stream_data in json.loads(response.text):
        stream_data = trimData(stream_data, Stream)
        streams_list.append(Stream(**stream_data))
    
    streams_list = [x for x in streams_list if x.type in streamTypes]
    return streams_list

def updateActivityDescription(activityID: int, description: str) -> dict:
    url = settings.base_url + "/activities/" + str(activityID)
    payload = {'description': description}
    headers = {'Authorization': 'Bearer ' + settings.access_token}
    
    response = makeRequest("PUT", url, headers=headers, data=payload)
    return json.loads(response.text)


def getSubscriptions() -> List[Subscription]:
    url = settings.base_url + "/push_subscriptions?client_id=" + str(settings.client_id) + "&client_secret=" + settings.client_secret

    response = requests.request("GET", url)
    subscription_list = []
    for subscription_data in json.loads(response):
        subscription_data = trimData(subscription_data, Subscription)
        subscription_list.append(Subscription(**subscription_data))
    return subscription_list


def createSubscription() -> dict:
    url = settings.base_url + "/push_subscriptions"

    payload = { 
        'client_id': settings.client_id,
        'client_secret': settings.client_secret,
        'callback_url': settings.webhook_callback_url + '/webhook',
        'verify_token': settings.webhook_verify_token
    }

    response = requests.request("POST", url, data=payload)
    return json.loads(response.text)


def deleteSubscription(subscriptionID):
    url = settings.base_url + "/push_subscriptions/" + str(subscriptionID)

    payload = {
        'client_id': str(settings.client_id),
        'client_secret': settings.client_secret
    }

    response = requests.request("DELETE", url, data=payload)
    if response.text != '':
        return json.loads(response.text)
    else:
        return ''

def getActivities(per_page: int, page: int) -> List[Activity]:
    url = settings.base_url + "/athlete/activities"
    headers = {'Authorization': 'Bearer ' + settings.access_token}
    params = {
        'per_page': str(per_page),
        'page': str(page)
    }

    response = makeRequest("GET", url, headers=headers, params=params)
    response = json.loads(response.text)
    activity_list: List[Activity] = []
    for activity_data in response:
        activity_data = trimData(activity_data, Activity)
        activity_data.setdefault("description", "")
        activity_list.append(Activity(**activity_data))
    return activity_list