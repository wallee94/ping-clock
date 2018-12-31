import json
import logging
from datetime import datetime

import boto3
import requests
from boto3.dynamodb.conditions import Attr

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def save_endpoint_history(endpoint_id, elapsed_time, status_code, start_timestamp):
    """
    saves enpoint status code and response elapsed time
    :param endpoint_id: str
    :param elapsed_time: float or None
    :param status_code: int
    :param start_timestamp: int
    :return: None
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('history')
    table.put_item(
        Item={
            "id": endpoint_id + '-' + str(start_timestamp),
            "timestamp": start_timestamp,
            "endpoint_url": endpoint_id,
            "status_code": status_code,
            "elapsed_time": elapsed_time
        }
    )
    logger.info('Saved new history for endpoint_id=[%s]', endpoint_id)


def lambda_handler(event, context):
    """
    ping the resource in event['url'] and trigger warning lambdas if the status code is different than 200
    :param event:
    :param context:
    :return:
    """
    url = event.get('url')
    endpoint_id = event.get('uuid')
    timestamp = int(datetime.now().timestamp())

    try:
        res = requests.get(url, timeout=1.5)

    except requests.exceptions.Timeout as e:
        logger.warning('Timeout requesting data from url=[%s]. %s', url, str(e.args))
        save_endpoint_history(endpoint_id, None, -1, timestamp)
        raise e

    if res.status_code == 200:
        return save_endpoint_history(endpoint_id, res.elapsed.total_seconds(), 200, timestamp)

    logger.warning('status_code=[%d] received from [%s]' , res.status_code, res.url)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('accounts')
    response = table.scan(
        FilterExpression=Attr('endpoint_set').contains(endpoint_id)
    )
    if not 'Items' in response:
        return

    # notify users about the status code received
    users = response['Items']
    lambda_client = boto3.client('lambda')
    for user in users:
        if not user.get('email'):
            continue

        payload = {
            'email': user['email'],
            'url': url,
            'status_code': res.status_code,
            'timestamp': timestamp
        }
        lambda_client.invoke(
            FunctionName='lambda_notifier',
            InvocationType='Event',
            LogType='None',
            Payload=json.dumps(payload),
        )

