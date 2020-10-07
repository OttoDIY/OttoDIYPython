#-- OttDIY Python Project, 2020

import json
import os

STOREDIR = '/eeprom'


def save(key, value):
    try:
        stat = os.stat(STOREDIR)
    except:
        os.mkdir(STOREDIR)

    filename = STOREDIR + '/' + key + '.json'
    f = open(filename, 'w')
    json_str = json.dumps(value)
    f.write(json_str)
    f.close()


def load(key, default = None):
    filename = STOREDIR + '/' + key + '.json'

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
