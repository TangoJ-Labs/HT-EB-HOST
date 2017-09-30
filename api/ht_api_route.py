##### APP ENDPOINTS #####

from flask import Blueprint, Flask, jsonify, redirect, render_template, request, send_file
from flask_assets import Environment
from flask_cors import CORS, cross_origin
from base64 import b64encode
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
from operator import itemgetter
from io import BytesIO
from PIL import Image
from urlparse import urlparse, urlunparse
import boto3
import calendar
import datetime
import decimal
import json
import random
import string
import time

# Import local
import ht_references
import ht_admin_lib
# import application as app


# RECALL THE HAZARD DATA
@application.route('/app/hazard/query', methods=['POST'])
def get_hazard():
  print("ROUTE: HAZARD ENDPOINT")
  # Retrieve the POST json parameters
  print(request.get_json(force=True))
  body = request.get_json(force=True)
  identity_id = body['identity_id']
  login_provider = body['login_provider']
  login_token = body['login_token']
  resource = ht_admin_lib.get_resource_with_credentials(identity_id, login_provider, login_token, 'dynamodb', 'us-east-1')

  # Retrieve the Hazard data
  table_hazard_name = 'Harvey-Hazard'
  table_hazard = resource.Table(table_hazard_name)
  table_hazard_index = 'status-timestamp-index'
  hazard_response = table_hazard.query(
    TableName=table_hazard_name
    , IndexName=table_hazard_index
    , KeyConditionExpression=Key('status').eq('active')
  )

  print("HAZARD RESPONSE:")
  print(hazard_response)
  return jsonify({'hazard' : hazard_response['Items']})

# TEST ENDPOINT
bp_api_test = Blueprint('bp_api_test', __name__)
@bp_api_test.route('/api/test', methods=['GET'])
def api_test():
  print("ROUTE: TEST API - MOVED")
  # Retrieve the POST json parameters
  # print(request.get_json(force=True))
  # body = request.get_json(force=True)
  identity_id = "us-east-1:3332d565-36ca-458c-80db-58fe85ef876f" #body['identity_id']
  login_provider = "graph.facebook.com" #body['login_provider']
  login_token = "EAACH6QOvruMBAKZCiPGZBMQpnoLZA77AkITLuEE2SvZAPGB504Bkr71TMAsm6xtZAoCmrCC7ZCkB2mvjI0ffHkTAjJiWAEqGN9gEXKGzOHa8i1EL5xmadbepB5nIfhQRo09HgAwr1cv6yzA7DIgJdXaEw7fl3SrAYZAtHb49rUeOPBFBv3cAm1oxWy1HUUUmJBPcnxPgmpSEhawcSZAN9RfrJL1GsRvOFToZD" #body['login_token']
  # session = ht_admin_lib.get_session_with_credentials(identity_id, login_provider, login_token, 'dynamodb')
  resource = ht_admin_lib.get_resource_with_credentials(identity_id, login_provider, login_token, 'dynamodb', 'us-east-1')
  # print(session.get_available_services())

  # Retrieve the Hazard data
  # hazard_response = dynamo.query(
  #   TableName=ht_references.table_hazard_name
  #   , IndexName=ht_references.table_hazard_index
  #   , KeyConditions={
  #       'status': {
  #           'AttributeValueList': [{
  #               'S': 'active',
  #           }]
  #           , 'ComparisonOperator': 'EQ'
  #       }
  #   }
  # )

  table_hazard_name = 'Harvey-Hazard'
  table_hazard = resource.Table(table_hazard_name)
  table_hazard_index = 'status-timestamp-index'
  hazard_response = table_hazard.query(
    TableName=table_hazard_name
    , IndexName=table_hazard_index
    , KeyConditionExpression=Key('status').eq('active')
  )
  print("HAZARD RESPONSE:")
  print(hazard_response['Items'])
  print("HAZARD RESPONSE JSONIFY:")
  print(jsonify(hazard_response['Items']))
  # json_conv = json_util.loads(hazard_response['Items'])
  # db_dict = dict(hazard_response['Items'])
  # print("HAZARD RESPONSE DICT:")
  # print(db_dict)
  # db_json = json.dumps(hazard_response['Items'])
  # print("HAZARD RESPONSE DUMPS:")
  # print(db_json)
  # json_conv = json.dumps(hazard_response['Items'])
  # print("HAZARD JSON CONV:")
  # print(json_conv)
  # return json.dumps(hazard_response)
  # return json.dumps({'hazard' : json_conv})
  return jsonify({'hazard' : hazard_response['Items']}) # Working in virtual env, not reg python? (harveyvenv)
