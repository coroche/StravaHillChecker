import requests
import json


def makeRequest(method, url, **kwargs):
    response = requests.request(method, url, **kwargs)
    if response.status_code == 401:
        newAccessToken = refreshTokens()
        kwargs['headers']['Authorization'] = 'Bearer ' + newAccessToken
        response = requests.request(method, url, **kwargs)
    return response


def readTokens():
    with open('config.json') as file:
        data = json.load(file)
    return data


def writeTokens(access_token, refresh_token):
    with open('config.json', 'r+') as file:
        data = json.load(file)
        data['access_token'] = access_token
        data['refresh_token'] = refresh_token
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()


def refreshTokens():    
    tokens = readTokens()
    url = tokens['base_url'] + "/oauth/token"

    payload={
        'client_id': tokens['client_id'],
        'client_secret': tokens['client_secret'],
        'grant_type': 'refresh_token',
        'refresh_token': tokens['refresh_token']
    }

    response = requests.request("POST", url, data=payload)
    response = json.loads(response.text)
    writeTokens(response['access_token'], response['refresh_token'])
    return response['access_token']


def getLoggedInAthlete():   
    tokens = readTokens()
    url = tokens['base_url'] + "/athlete"
    headers = {'Authorization': 'Bearer ' + tokens['access_token']}

    response = makeRequest("GET", url, headers=headers)
    return json.loads(response.text)


def getLoggedInAthleteActivities():   
    tokens = readTokens()
    url = tokens['base_url'] + "/athlete/activities"
    headers = {'Authorization': 'Bearer ' + tokens['access_token']}
    params = {
        'per_page': 20,
        'page': 1
    }

    response = makeRequest("GET", url, headers=headers, params=params)
    return json.loads(response.text)


def getActivityById(activityID):   
    tokens = readTokens()
    url = tokens['base_url'] + "/activities/" + str(activityID)
    headers = {'Authorization': 'Bearer ' + tokens['access_token']}

    response = makeRequest("GET", url, headers=headers)
    return json.loads(response.text)


def getActivityStreams(activityID, streamTypes):   
    tokens = readTokens()
    url = tokens['base_url'] + "/activities/" + str(activityID) + "/streams"
    streamTypes = str(streamTypes).replace("'","").replace(" ","")[1:-1]
    headers = {'Authorization': 'Bearer ' + tokens['access_token']}
    params = {'keys': streamTypes}

    response = makeRequest("GET", url, headers=headers, params=params)
    return json.loads(response.text)

def updateActivityDescription(activityID, description):   
    tokens = readTokens()
    url = tokens['base_url'] + "/activities/" + str(activityID)
    payload = {'description': description}
    headers = {'Authorization': 'Bearer ' + tokens['access_token']}
    
    response = makeRequest("PUT", url, headers=headers, data=payload)
    return json.loads(response.text)


def getSubscriptions():   
    tokens = readTokens()
    url = tokens['base_url'] + "/push_subscriptions?client_id=" + str(tokens['client_id']) + "&client_secret=" + tokens['client_secret']

    response = requests.request("GET", url)
    return json.loads(response.text)


def createSubscription():  
    tokens = readTokens()
    url = tokens['base_url'] + "/push_subscriptions"

    payload = {'client_id': tokens['client_id'],
    'client_secret': tokens['client_secret'],
    'callback_url': tokens['webhook_callback_url'] + '/webhook',
    'verify_token': tokens['webhook_verify_token']}

    response = requests.request("POST", url, data=payload)
    return json.loads(response.text)


def deleteSubscription(subscriptionID):
    tokens = readTokens()
    url = tokens['base_url'] + "/push_subscriptions/" + str(subscriptionID)

    payload = {'client_id': str(tokens['client_id']),
    'client_secret': tokens['client_secret']}

    response = requests.request("DELETE", url, data=payload)
    if response.text != '':
        return json.loads(response.text)
    else:
        return ''
