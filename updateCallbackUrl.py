import json
import requests

def writeCallBackUrl(callback_url):
    with open('tokens.json', 'r+') as file:
        data = json.load(file)
        data['webhook_callback_url'] = callback_url
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()

def getWebhookCallbackUrl():
    url = "http://localhost:4040/api/tunnels/"
    
    response = requests.request("GET", url)
    response = json.loads(response.text)
    webhook_callback_url = response['tunnels'][0]['public_url']
    writeCallBackUrl(webhook_callback_url)

if __name__ == "__main__":
    getWebhookCallbackUrl()