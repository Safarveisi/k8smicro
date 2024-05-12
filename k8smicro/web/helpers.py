import os
from typing import Tuple

import psycopg
import boto3
from botocore.client import ClientError

# K8s service DNS name
POSTGRES_SERVICE_DNS_NAME = 'postgres.default.svc.cluster.local'
POSTGRES_HOST_PORT = f'{POSTGRES_SERVICE_DNS_NAME}:5432'
DB_URL = f'postgresql://ps_user:SecurePassword@{POSTGRES_HOST_PORT}/ps_db'


class S3Handler():

    def __init__(self) -> None:
        '''
        Assuming that some env variables are already set
        '''
        self.s3 = boto3.resource(
            service_name='s3',
            region_name=os.environ['AWS_DEFAULT_REGION'],
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            endpoint_url=os.environ['S3_ENDPOINT_URL']
        )

        self.bucket = self.s3.Bucket(os.environ['S3_BUCKET'])

    def check_connection(self) -> Tuple[bool, str]:
        '''Checks the access to the s3 bucket'''
        try:
            self.s3.meta.client.head_bucket(Bucket=self.bucket.name)
            return True, 'Access to bucket successful'
        except ClientError:
            return False, 'The bucket does not exist or you have no access'

def exists_in_postgres_table(
    month: str, day: str
) -> None | int:
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            query = f'''
                SELECT 
                    failed
                FROM stats
                WHERE 
                    month = {month!r} AND
                    day = {day!r} 
            '''
            cur.execute(query)
            row = cur.fetchone()
    return row[0] if row else None


def create_postgres_table() -> None:
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            query = f'''
            CREATE TABLE IF NOT EXISTS stats (
                month VARCHAR(255) NOT NULL,
                day VARCHAR(255) NOT NULL,
                failed INT NOT NULL
            )
            '''
            cur.execute(query)
            conn.commit()


def insert_into_postgres_table(
    month: str,
    day: str,
    failed: int
) -> None:
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            query = f'''INSERT INTO stats(month,day,failed)
                        VALUES(%s)'''
            cur.execute(query, (month, day, failed))
            conn.commit()
