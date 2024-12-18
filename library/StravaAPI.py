import requests
import json
from data import config
from data.userDAO import User
from typing import List
from dataclasses import dataclass, field
from datetime import datetime, timezone
from library.googleSheetsAPI import Hill
from utils.decorators import trim

@trim
@dataclass
class Activity:
    id: int
    name: str
    start_date: str
    start_date_local: str
    sport_type: str
    distance: float
    moving_time: float
    total_elevation_gain: float
    visibility: str
    private: bool
    kudos_count: int
    description: str = ''
    hills: List[Hill] = field(default_factory=list)

    @property
    def custom_description(self):
        old_description = self.description
        if old_description is None:
            old_description = ""
        if old_description != "" and 'VLs:' in old_description:
            old_description = old_description[0:old_description.find('VLs:')].rstrip()
        return old_description
    
    @property
    def activity_date_local(self):
        return datetime.strptime(self.start_date_local, '%Y-%m-%dT%H:%M:%S%z')
    
    @property
    def activity_date_utc(self):
        return datetime.strptime(self.start_date, '%Y-%m-%dT%H:%M:%S%z')

@trim
@dataclass
class Athlete:  
    firstname: str
    lastname: str
    id: int = 0

    @property
    def fullname(self) -> str:
        return self.firstname + self.lastname


@trim
@dataclass
class Stream:
    type: str
    data: List[List[float]]


@trim
@dataclass
class Subscription:
    id: int
    callback_url: str


@trim
@dataclass
class TokenResponse:
    access_token: str
    refresh_token: str
    expires_in: int

@trim
@dataclass
class ActivityPhoto:
    activity_id: str
    urls: dict
    default_photo: bool


settings = config.getConfig()

def makeRequest(method: str, url: str, user: User, **kwargs) -> requests.Response:
    if user.strava_token_expiry < datetime.now(timezone.utc) or (response:=requests.request(method, url, **kwargs)).status_code == 401:
        tokens = getNewTokens(user)
        user.updateStravaTokens(tokens.access_token, tokens.refresh_token, tokens.expires_in)
        kwargs['headers']['Authorization'] = 'Bearer ' + user.strava_access_token
        response = requests.request(method, url, **kwargs)
    return response


def getNewTokens(user: User) -> TokenResponse:
    url = settings.base_url + "/oauth/token"

    payload={
        'client_id': settings.client_id,
        'client_secret': settings.client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': user.strava_refresh_token
    }

    response = requests.request("POST", url, data=payload)
    if response.status_code != 200:
        raise RuntimeError("Invalid refresh token. User reauthorization required.")
    
    token_data = json.loads(response.text)
    tokens = TokenResponse(**token_data)
    
    return tokens
    

def getLoggedInAthlete(user: User) -> Athlete:
    url = settings.base_url + "/athlete"
    headers = {'Authorization': 'Bearer ' + user.strava_access_token}

    response = makeRequest("GET", url, user, headers=headers)
    athlete_data: dict = json.loads(response.text)
    return Athlete(**athlete_data)


def getActivities(user: User, per_page: int, page: int) -> List[Activity]:
    url = f"{settings.base_url}/athlete/activities"
    headers = {'Authorization': 'Bearer ' + user.strava_access_token}
    params = {
        'per_page': str(per_page),
        'page': str(page)
    }

    response = makeRequest("GET", url, user, headers=headers, params=params)
    activity_list: List[Activity] = [Activity(**activity_data) for activity_data in json.loads(response.text)]
    return activity_list


def getActivityById(user: User, activityID: int) -> Activity | None:
    url = f"{settings.base_url}/activities/{activityID}"
    headers = {'Authorization': 'Bearer ' + user.strava_access_token}

    response = makeRequest("GET", url, user, headers=headers)
    if response.status_code == 404:
        return None
    activity_json: dict = json.loads(response.text)
    activity = Activity(**activity_json)
    return activity


def getActivityStreams(user: User, activityID: int, streamTypes: List[str]) -> List[Stream]:
    url = f"{settings.base_url}/activities/{activityID}/streams"
    streamTypes_str = str(streamTypes).replace("'","").replace(" ","")[1:-1]
    
    headers = {'Authorization': 'Bearer ' + user.strava_access_token}
    params = {'keys': streamTypes_str}

    response = makeRequest("GET", url, user, headers=headers, params=params)  
    
    streams_list = [Stream(**stream_data) for stream_data in json.loads(response.text)]
    streams_list = [stream for stream in streams_list if stream.type in streamTypes]
    return streams_list


def getPrimaryActivityPhoto(user: User, activityID: int) -> str:
    url = f"{settings.base_url}/activities/{activityID}/photos"
    headers = {'Authorization': 'Bearer ' + user.strava_access_token}
    params = {'size': 5000}

    response = makeRequest("GET", url, user, headers=headers, params=params)
    if response.status_code == 404:
        return settings.default_email_image
    
    photo_list = [ActivityPhoto(**photo_data) for photo_data in json.loads(response.text)]
    primary_photo = [photo for photo in photo_list if photo.default_photo]
    if len(primary_photo) == 0:
        return settings.default_email_image
    else:
        url = primary_photo[0].urls['5000']
        if url:
            return url
        else:
            return settings.default_email_image


def getActivityKudoers(user: User, activityID: int, kudos_count: int) -> List[Athlete]:
    url = f"{settings.base_url}/activities/{activityID}/kudos"
    
    headers = {'Authorization': 'Bearer ' + user.strava_access_token}
    params = {'per_page': kudos_count}

    response = makeRequest("GET", url, user, headers=headers, params=params)    
    kudos_list = [Athlete(**kudos_data) for kudos_data in json.loads(response.text)]  
    return kudos_list


def updateActivityDescription(user: User, activityID: int, description: str) -> Activity:
    url = settings.base_url + "/activities/" + str(activityID)
    payload = {'description': description}
    headers = {'Authorization': 'Bearer ' + user.strava_access_token}
    
    response = makeRequest("PUT", url, user, headers=headers, data=payload)

    activity_json: dict = json.loads(response.text)
    activity = Activity(**activity_json)
    return activity


def getSubscriptions() -> List[Subscription]:
    url = settings.base_url + "/push_subscriptions"

    params = { 
        'client_id': settings.client_id,
        'client_secret': settings.client_secret,
    }

    response = requests.request("GET", url, params=params)
    subscription_list = [Subscription(**subscription_data) for subscription_data in json.loads(response.text)]
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

