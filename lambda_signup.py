import json
import logging
import uuid

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
    register a new account using a social media token
    """
    body = json.loads(event['body'])
    social_id = body.get('socialId')
    social_token = body.get('socialToken')
    social_media = body.get('socialMedia')
    email = body.get('email')

    if not social_id or not social_media or not social_token or not email:
        return respond(ValueError('socialId, socialToken, socialMedia and email are required'))

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('accounts')
    user_uuid = uuid.uuid4()
    table.put_item(Item={
        "uuid": user_uuid,
        "social_account_id": social_id,
        "social_account_token": social_token,
        "social_media": social_media,
        "email": email,
        "is_premium": False,
        "endpoint_set": []
    })

    return respond(None, {'uuid': user_uuid})
