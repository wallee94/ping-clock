import json
import uuid
from datetime import datetime

import boto3


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.args if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
    """
    register a new endpoint to ping every 6 minutes
    """
    body = json.loads(event['body'])
    url = body.get('url')
    account_uuid = body.get('accountUUID')
    if not url or not account_uuid:
        return respond(ValueError('url and accountUUID are required'))

    dynamodb = boto3.resource('dynamodb')
    # search if account really exists
    table = dynamodb.Table('accounts')
    response = table.get_item(Key={'uuid': account_uuid})
    if 'Item' not in response:
        return respond(ValueError("account doesn't exist"))

    # parse url to get domain
    if not url.startwith('http'):
        url = "http://" + url

    if not url.endswith('/'):
        url += '/'
    
    # search url in our current database
    domain = url.split('/')[2]
    table = dynamodb.Table('endpoints')
    url_uuid = str(uuid.uuid3(uuid.NAMESPACE_URL, url))
    response = table.get_item(Key={'uuid': uuid})    
    if 'Item' not in response:
        # save url if it doesn't exist
        table.put_item(Item={
            'uuid': url_uuid,
            'url': url,
            'domain': domain,
            'created_at': datetime.now().timestamp(),
            'updated_at': datetime.now().timestamp(),
        })

    return respond(None, {'status': 'OK'})
