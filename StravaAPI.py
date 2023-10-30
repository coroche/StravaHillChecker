import requests
import json
import config
from typing import List


class Activity:
    def __init__(self, data: dict):
        self.id: int = data.get("id")
        self.name: str = data.get("name")
        self.description: str = data.get("description")
        self.start_date_local: str = data.get("start_date_local")
        self.sport_type: str = data.get("sport_type")


class Athlete:
    def __init__(self, data: dict):
        self.id = data.get("id")
        self.firstname = data.get("firstname")
        self.lastname = data.get("lastname")


class Stream:
    def __init__(self, data: dict):
        self.type: str = data.get("type")
        self.data: List[List[float]] = data.get("data")


class Subscription:
    def __init__(self, data: dict):
        self.id: int = data.get("id")


class TokenResponse:
    def __init__(self, data: dict):
        self.access_token: str = data.get("access_token")
        self.refresh_token: str = data.get("refresh_token")


settings = config.getConfig()


def makeRequest(method: str, url: str, **kwargs) -> requests.Response:
    response = requests.request(method, url, **kwargs)
    if response.status_code == 401:
        refreshTokens()
        kwargs['headers']['Authorization'] = 'Bearer ' + settings.access_token
        response = requests.request(method, url, **kwargs)
    return response


def writeTokens():
    with open('config.json', 'r+') as file:
        data = json.load(file)
        data['access_token'] = settings.access_token
        data['refresh_token'] = settings.refresh_token
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()


def refreshTokens():
    url = settings.base_url + "/oauth/token"

    payload={
        'client_id': settings.client_id,
        'client_secret': settings.client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': settings.refresh_token
    }

    response = requests.request("POST", url, data=payload)
    tokens = TokenResponse(json.loads(response.text))    
    
    settings.access_token = tokens.access_token
    settings.refresh_token = tokens.refresh_token

    writeTokens()


def getLoggedInAthlete() -> Athlete:
    url = settings.base_url + "/athlete"
    headers = {'Authorization': 'Bearer ' + settings.access_token}

    response = makeRequest("GET", url, headers=headers)
    athlete_data = json.loads(response.text)
    return Athlete(athlete_data)


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
    activity = Activity(json.loads(response.text))
    return activity


def getActivityStreams(activityID: int, streamTypes: List[str]) -> List[Stream]:
    url = settings.base_url + "/activities/" + str(activityID) + "/streams"
    streamTypes_str = str(streamTypes).replace("'","").replace(" ","")[1:-1]
    
    headers = {'Authorization': 'Bearer ' + settings.access_token}
    params = {'keys': streamTypes_str}

    response = makeRequest("GET", url, headers=headers, params=params)  
    streams_list: List[Stream] = []
    for stream_data in json.loads(response.text):
        streams_list.append(Stream(stream_data))
    
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
        subscription_list.append(Subscription(subscription_data))
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
        activity_list.append(Activity(activity_data))
    return activity_list