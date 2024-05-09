import os
import time
import json
import requests
import logging

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename='failed_attrs.log', format=log_format, level=logging.INFO)

DATA = \
[
    {
        "month": "5",
        "day": "5"
    },
    {
        "month": "5",
        "day": "6"
    },
    {
        "month": "5",
        "day": "4"
    },
    {
        "month": "5",
        "day": "3"
    }
]

# Post request payload
JSON_DATA = json.dumps(DATA)

# K8s service DNS name
SERVICE_DNS_NAME = 'web-service.default.svc.cluster.local'
BASE_URL = f'http://{SERVICE_DNS_NAME}:80'

logging.info('Checking the s3 connection')

response = requests.get(BASE_URL+'/health/')

if response.status_code == 200:
    response_dict = response.json()
    if response_dict['success']:
        logging.info(response_dict['msg'])
        logging.info('Analysing dill files for the requested times ...')
        response = requests.post(
            BASE_URL+'/failed_stats/', 
            data=JSON_DATA, 
            timeout=20
            )
        logging.info('Writing the response into result.json')
        with open('result.json', 'w') as f:
            json.dump(response.json(), f)
    else:
        logging.info(response_dict['msg'])
        logging.info('Skipe analysing')
        exit(1)
else:
    print(f'Get request failed with status code: {response.status_code}')

