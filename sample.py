# Micropython embeded libraries
import os
import time
import json
# micropython-lib/python-stdlib/
import copy
# micropython-lib/python-ecosys/
import requests

print('Hello World!')
print(f'Current working directory: {os.getcwd()}')
print(f'Current time: {time.time()}')

sample_dict = {
    'foo': 'bar',
    'baz': 'qux',
}
new_dict = copy.deepcopy(sample_dict)
sample_dict['foo'] = 'baz'

print(f'Original dict: {sample_dict}')
print(f'Copied dict: {new_dict}')
print(f'JSON encoded dict: {json.dumps(sample_dict)}')

print('Requesting https://www.google.com...')
response = requests.get('https://www.google.com')
print(f'Response status code: {response.status_code}')
