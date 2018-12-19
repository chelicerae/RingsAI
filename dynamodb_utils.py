import boto3
import datetime
from botocore.exceptions import ClientError


def push_record(table, pkey_id, account_name, data):
    response = table.put_item(
        Item={
            'id': pkey_id,
            'account_name': account_name,
            'timestamp': datetime.datetime.now().isoformat(),
            'analyzed': data
        }
    )


def check_record(table, pkey_id):
    try:
        response = table.get_item(
            Key={'id': pkey_id}
        )
        response['Item']
        return True, response
    except KeyError:
        return False, {}

# if __name__ == '__main__':
#     client = boto3.resource('dynamodb', aws_access_key_id='AKIAIVMLI3XEBFYF4ZWQ',
#                             aws_secret_access_key='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', region_name='us-east-2')
#     table = client.Table('PinterestAnalyzer')