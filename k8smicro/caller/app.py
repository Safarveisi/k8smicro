import json
import requests
import logging
from typing import List

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename='failed_attrs.log', format=log_format, level=logging.INFO)

class AnalyseRequest(BaseModel):
    month: str
    day: str

# K8s service DNS name
SERVICE_DNS_NAME = 'web-service.default.svc.cluster.local'
BASE_URL = f'http://{SERVICE_DNS_NAME}:80'

app = FastAPI()

@app.get('/health/', status_code=200)
async def s3_health_check() -> dict:
    '''Checks the S3 connection'''
    logging.info('Requested s3 health check')
    response = requests.get(BASE_URL+'/health/')
    if response.status_code == 200:
        response_dict = response.json()
        logging.info(response_dict['msg'])
        return response_dict
    else:
        msg = 'Get http request failed due to an internal error'
        logging.info(msg)
        return {'msg': msg}

@app.post('/failed_stats/', status_code=200)
async def analyse_dill_files(times: List[AnalyseRequest]) -> List[dict] | dict:
    '''
    Retuns the number of rows in a pandas dataframe  
    whose 'failed_attrs' attribute is not empty for
    the requested times.
    '''
    logging.info('Analysing dill files for the requested times ...')
    data = [time.dict() for time in times]
    json_data = json.dumps(data)
    response = await requests.post(
        BASE_URL+'/failed_stats/', 
        data=json_data, 
    )
    if response.status_code == 200:
        logging.info('Finished analysing')
        return response.json()
    else:
        msg = 'Post http request failed due to an internal error'
        logging.info(msg)
        return {'msg': msg}

if __name__ == '__main__':

    uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')