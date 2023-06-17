import json

def get(parameter):
    with open('config.json') as file:
        data = json.load(file)
    return data[parameter]

def write(parameter, value):
    with open('config.json', 'r+') as file:
        data = json.load(file)
        data[parameter] = value
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()