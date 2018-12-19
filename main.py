# !/usr/bin/env python
import json
from multiprocessing import Process

import boto3
from flask import Flask, render_template, request

from config import SQS_QUEUE_NAME
from dynamodb_utils import check_record
from main_scraper import analyze_account
from sqs_utils import get_queue_url, start_reciever, send_message_sqs

app = Flask(__name__)

client_sqs = boto3.client('sqs')
client_dynamo = boto3.resource('dynamodb', region_name='us-east-2')

sqs_queue_url = get_queue_url(client_sqs, SQS_QUEUE_NAME)


@app.before_first_request
def prepare_server():
    # start_reciever(client_sqs, sqs_queue_url)

    p = Process(target=start_reciever, args=(client_sqs, sqs_queue_url))

    p.start()

@app.route('/')
def index():
    return render_template('pinterest_form.html')


#
# @app.route('/analyze', methods=['POST'])
# def analyze():
#     pinterest_account = request.form["account_name"]
#
#     account_info = send_message_sqs(client_sqs, pinterest_account)
#
#     try:
#         data_analyzed = analyze_account(pinterest_account)
#     except EOFError as eof:
#         return render_template('error.html', error=eof)
#     except BaseException as ex:
#         return render_template('error.html', error=ex)
#
#     # clusters_to_render = get_cluster_labels_mapping(insta_clusters['clusters'])
#
#     # rings = get_preffered_ring_types(insta_clusters['clusters'])
#     if len(data_analyzed) == 0:
#         return render_template('error.html', error='Not a pinterest board')
#     return render_template('board_info.html', board_link=pinterest_account, colors=data_analyzed['COLORS'],
#                            stone_shapes=data_analyzed['STONE_SHAPES'], ring_types=data_analyzed['RING_TYPES'],
#                            stone_types=data_analyzed['STONE_TYPES'], ring_materials=data_analyzed['RING_MATERIALS'])

@app.route('/api/analyze', methods=['GET'])
def api_analyze():
    try:
        pinterest_account = request.args.get('pinterest_account')
        account_info = send_message_sqs(client_sqs, sqs_queue_url, pinterest_account)

        if len(pinterest_account) > 0:
            response = app.response_class(
                response=json.dumps({"code": 200, "data": account_info}),
                status=200
            )
        else:
            response = app.response_class(
                response=json.dumps({"code": 400, 'error': True, 'message': 'Invalid account name'}),
                status=400
            )
    except TypeError as e:
        response = app.response_class(
            response=json.dumps({"code": 400, 'error': True, 'message': 'Empty account name'}),
            status=400
        )

    return response


def preprocess_response(response_data):
    item = response_data['Item']

    analyzed = item['analyzed']

    new_analyzed = {}
    for property, values in analyzed.items():
        new_values = {}
        for category, value in values.items():
            new_values[category] = int(value)
        new_analyzed[property] = new_values

    item['analyzed'] = new_analyzed
    response_data['Item'] = item

    return response_data

@app.route('/api/is_analyzed', methods=['GET'])
def is_analyzed():
    try:
        id = request.args.get('id')
        table = client_dynamo.Table('PinterestAnalyzer')

        is_processed, response_data = check_record(table, id)

        print('response_data', response_data)
        print('is_processed', is_processed)

        if is_processed:

            response_data = preprocess_response(response_data)
            response = app.response_class(
                response=json.dumps({"code": 200, "data": response_data}),
                status=200
            )
        else:
            response = app.response_class(
                response=json.dumps({"code": 200, "data": 'No data available. Please try later'}),
                status=200
            )
    except TypeError as e:
        print('Error', e)
        response = app.response_class(
            response=json.dumps({"code": 400, 'error': True, 'message': 'Empty id name'}),
            status=400
        )

    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0')
