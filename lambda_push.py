import json

import boto3


def lambda_handler(event, context):
    """
    trigger all ping lambdas from endpoints in dynamodb table
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('endpoints')

    response = table.scan()
    endpoints = response['Items']

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        endpoints.extend(response['Items'])

    lambda_client = boto3.client('lambda')
    for endpoint in endpoints:
        payload = {
            'url': endpoint['url'],
            'uuid': endpoint['uuid']
        }
        lambda_client.invoke(
            FunctionName='lambda_ping',
            InvocationType='Event',
            LogType='None',
            Payload=json.dumps(payload),
        )
