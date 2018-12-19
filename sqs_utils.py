import json

import boto3
# create a boto3 client
# create the test queue
# client.create_queue(QueueName='test_ids')
from dynamodb_utils import push_record
from main_scraper import analyze_account


client_dynamo = boto3.resource('dynamodb', aws_access_key_id='AKIAIVMLI3XEBFYF4ZWQ', aws_secret_access_key='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', region_name='us-east-2')


def get_queue_url(client, queue_name):
    queues = client.list_queues(QueueNamePrefix=queue_name)  # we filter to narrow down the list
    queue_url = queues['QueueUrls'][0]

    return queue_url

def start_reciever(client, queue_url):
    print('Started SQS Reciever')
    while True:
        messages = client.receive_message(QueueUrl=queue_url,
                                          MaxNumberOfMessages=10)  # adjust MaxNumberOfMessages if needed
        if 'Messages' in messages:  # when the queue is exhausted, the response dict contains no 'Messages' key
            for message in messages['Messages']:  # 'Messages' is a list
                # process the messages
                pinterest_account = message['Body']
                print('Message whole', message)
                print('Pinterest account is', pinterest_account)
                # next, we delete the message from the queue so no one else will process it again
                data_analyzed = analyze_account(pinterest_account)

                with open('data_analyzed.json', 'w') as f:
                    json.dump(data_analyzed, f)

                print('Data analyzed', data_analyzed)

                table = client_dynamo.Table('PinterestAnalyzer')

                push_record(table, message['MessageId'], pinterest_account, data_analyzed)

                client.delete_message(QueueUrl=queue_url, ReceiptHandle=message['ReceiptHandle'])
        else:
            pass


def send_message_sqs(client, queue_url, account_name):
    enqueue_response = client.send_message(QueueUrl=queue_url, MessageBody=account_name)

    account_id = enqueue_response['MessageId']
    print('Message ID : ', enqueue_response['MessageId'])

    return {'id': account_id, 'name': account_name}

# if __name__ == '__main__':
#     client = boto3.client('sqs')
#
#     url = get_queue_url(client, 'test_ids')
#     print(url)