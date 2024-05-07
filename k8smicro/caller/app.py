import os
import time
import json
import requests

# K8s service DNS name
SERVICE_DNS_NAME = 'web-service.default.svc.cluster.local'
URL = f'http://{SERVICE_DNS_NAME}:80/health/'

for i in range(1000):

    response = requests.get(URL)

    if response.status_code == 200:
        print('Get request successful')
        response_dict = json.loads(response.content.decode('utf-8'))
        with open(
            os.path.join(os.path.abspath(os.getcwd()),
                         f'response_{i}.json'), 'w'
        ) as json_file:
            json.dump(response_dict, json_file)
    else:
        print(f'Get request failed with status code: {response.status_code}')

    time.sleep(3)
