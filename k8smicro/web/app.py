import logging
from typing import List

import helpers

import dill
import uvicorn
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)

handlers = {}
requested_times = {}


class AnalyseRequest(BaseModel):
    month: str
    day: str


async def get_service_handlers():
    global handlers
    handlers['s3'] = helpers.S3Handler()
    logging.info('S3 resource service client established')


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_service_handlers()
    logging.info('Updated global service handlers')
    yield
    handlers.clear()
    logging.info('Released resources')

app = FastAPI(lifespan=lifespan)


async def count_row_with_failed_attrs(month: str, day: str) -> int | None:
    '''
    Gets all the dill files from a s3 bucket for the given month and day,
    converts them into a pandas dataframe and counts the number of rows 
    whose failed_attrs column is not "empty". 
    '''
    global handlers
    global requested_times

    # Check the cache
    if (month, day) in requested_times:
        return requested_times[(month, day)]

    list_df_validation = []
    objects = handlers['s3'].bucket.objects.filter(
        Prefix=f'advanced-analytics/fraudml/mrrp_live_ftr_vectors'
        f'/2024_{month.zfill(2)}_{day.zfill(2)}')

    if next(objects.pages()):
        # Total number of failed rows
        num_rows_failed = 0
        for obj in objects:
            d: dict = dill.load(obj.get()['Body'])
            list_df_validation.append(d['df_validation'])
        # Increment num_rows_failed with the number of rows found
        num_rows_failed += pd.concat(list_df_validation, axis=0) \
            .query("failed_attrs != 'empty'").shape[0]
        requested_times[(month, day)] = num_rows_failed
        return num_rows_failed
    else:
        return None


@app.get('/health/', status_code=200)
async def s3_health_check():
    '''Checks the S3 connection'''
    global handlers
    return {
        'serviceStatus': 'OK',
        'S3ConnectionHealth': handlers['s3'].check_connection()
    }


@app.post('/failed_stats/', status_code=200)
async def analyse_dill_files(times: List[AnalyseRequest]):
    '''
    Retuns the number of rows in a pandas dataframe  
    whose 'failed_attrs' attribute is not empty for
    the requested times.
    '''
    stats = []
    for time in times:
        request_and_result = {}
        request_and_result['request'] = time.dict()
        result = await count_row_with_failed_attrs(
            time.month, time.day)
        request_and_result['result'] = \
            "Did not find any dill files for the requested time" \
            if result is None else result
        stats.append(request_and_result)
    return stats


if __name__ == '__main__':

    uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')
