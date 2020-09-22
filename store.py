import json
import os

def save(key, value):
    filename = '/user/' + key + '.json'
    f = open(filename, 'w')
    json_str = json.dumps(value)
    f.write(json_str)
    f.close()

def load(key, default = None):
    filename = '/user/' + key + '.json'

    try:
        f = open(filename)
        json_str = f.read()
        value = json.loads(json_str)
        f.close()
        return value
    except:
        if default == None:
            raise ValueError()
        return default
