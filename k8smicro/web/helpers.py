import os

import boto3
from botocore.client import ClientError


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

    def check_connection(self) -> str:
        '''Checks the access to the s3 bucket'''
        try:
            self.s3.meta.client.head_bucket(Bucket=self.bucket.name)
            return 'Access to bucket successful'
        except ClientError:
            return 'The bucket does not exist or you have no access'
