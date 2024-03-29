#-- OttDIY Python Project, 2020
#
# import json
# import os
#
# STOREDIR = '/eeprom'
#
#
# def save(key, value):
#     try:
#         stat = os.stat(STOREDIR)
#     except:
#         os.mkdir(STOREDIR)
#
#     filename = STOREDIR + '/' + key + '.json'
#     f = open(filename, 'w')
#     json_str = json.dumps(value)
#     f.write(json_str)
#     f.close()
#
#
# def load(key, default = None):
#     filename = STOREDIR + '/' + key + '.json'
#
#     try:
#         f = open(filename)
#         json_str = f.read()
#         value = json.loads(json_str)
#         f.close()
#         return value
#     except:
#         if default == None:
#             raise ValueError()
#         return default

import json
import os
from esp32 import NVS


def save(key, value, namespace='Eeprom'):
    nvs = NVS(namespace)
    json_str = json.dumps(value)
    nvs.set_blob(key, json_str)

    # don't forget to commit
    nvs.commit()


def load(key, default=None, namespace='Eeprom'):
    nvs = NVS(namespace)
    buf = bytearray(1000)

    try:
        nvs.get_blob(key, buf)
        value = json.loads(buf)
        return value
    except Exception as _:
        if default is None:
            raise ValueError()
        return default
