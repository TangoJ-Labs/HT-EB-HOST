##### API ENDPOINTS #####

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
import importlib
import random
import string
import time

# Import local
import ht_references
# import ht_admin_lib
# import application as app


# RECALL THE APP SETTINGS
bp_api_app_settings = Blueprint('bp_api_app_settings', __name__)
@bp_api_app_settings.route('/' + ht_references.route_api_app_settings, methods=['POST'])
def app_settings():
  print("ROUTE: API - APP SETTINGS")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    # Replace the periods in the version name to underscores (to match the package name)
    app_version_mod = body['app_version'].replace('.', '_')
    # import the module needed from the package that matches the version name
    util = importlib.import_module('..v' + app_version_mod + '.ht_api_lib_util', 'api.subpkg')
    response['settings'] = util.app_settings()
    response['response'] = 'success'
  return jsonify(response)

# RECALL IMAGE DATA
bp_api_image_data = Blueprint('bp_api_image_data', __name__)
@bp_api_image_data.route('/' + ht_references.route_api_image_data, methods=['POST'])
def api_image_data():
  print("ROUTE: API - IMAGE DATA")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    # Replace the periods in the version name to underscores (to match the package name)
    app_version_mod = body['app_version'].replace('.', '_')
    # import the module needed from the package that matches the version name
    util = importlib.import_module('..v' + app_version_mod + '.ht_api_lib_util', 'api.subpkg')
    response['image_data'] = util.image_data(body)
    response['request'] = body
    response['response'] = 'success'
  return jsonify(response)

# RETURN ALL SKILLS FOR THE PASSED USER
bp_api_skill_query = Blueprint('bp_api_skill_query', __name__)
@bp_api_skill_query.route('/' + ht_references.route_api_skill_query, methods=['POST'])
def api_skill_query():
  print("ROUTE: API - SKILL QUERY")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    util = importlib.import_module('..v' + app_version_mod + '.ht_api_lib_util', 'api.subpkg')
    response['skills'] = util.skill_query(body)
    response['response'] = 'success'
  return jsonify(response)

# RETURN ALL STRUCTURES FOR THE PASSED USER
bp_api_structure_query = Blueprint('bp_api_structure_query', __name__)
@bp_api_structure_query.route('/' + ht_references.route_api_structure_query, methods=['POST'])
def api_structure_query():
  print("ROUTE: API - STRUCTURE QUERY")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    util = importlib.import_module('..v' + app_version_mod + '.ht_api_lib_util', 'api.subpkg')
    query_response = util.structure_query(body)
    if query_response['result'] == 'success':
      response['structures'] = query_response['structures']
      response['response'] = 'success'
  return jsonify(response)

# RETURN ALL STRUCTURE USERS FOR THE PASSED STRUCTURE OR USER, WHICHEVER WAS PASSED
bp_api_structure_user_query = Blueprint('bp_api_structure_user_query', __name__)
@bp_api_structure_user_query.route('/' + ht_references.route_api_structure_user_query, methods=['POST'])
def api_structure_user_query():
  print("ROUTE: API - STRUCTURE-USER QUERY")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    util = importlib.import_module('..v' + app_version_mod + '.ht_api_lib_util', 'api.subpkg')
    response['structure_users'] = util.structure_user_query(body)
    response['response'] = 'success'
  return jsonify(response)

# RETURN ALL REPAIRS FOR THE PASSED STRUCTURE ID
bp_api_repair_query = Blueprint('bp_api_repair_query', __name__)
@bp_api_repair_query.route('/' + ht_references.route_api_repair_query, methods=['POST'])
def api_repair_query():
  print("ROUTE: API - REPAIR QUERY")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  print(body)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    util = importlib.import_module('..v' + app_version_mod + '.ht_api_lib_util', 'api.subpkg')
    query_response = util.repair_query(body)
    if query_response['result'] == 'success':
      response['repairs'] = query_response['repairs']
      response['repair_settings'] = ht_references.repair_list
      response['response'] = 'success'
    # Loop through the structure users and add the facebook data needed
    for uIndex, user in enumerate(body['structure']['users']):
      updated_user_data = util.user_query(user['user_id'])
      print("REPAIR QUERY OLD USER:")
      print(body['structure']['users'][uIndex])
      print("REPAIR QUERY UPDATED USER:")
      print(updated_user_data)
      body['structure']['users'][uIndex] = updated_user_data
    # Return the updated data
    response['request'] = body
    print("REPAIR QUERY REQUEST RETURN:")
    print(response['request'])
  return jsonify(response)

# RECALL THE SPOT DATA
bp_api_spot_query_active = Blueprint('bp_api_spot_query_active', __name__)
@bp_api_spot_query_active.route('/' + ht_references.route_api_spot_query_active, methods=['POST'])
def api_spot_query_active():
  print("ROUTE: SPOT QUERY ACTIVE")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    print(app_version_mod)
    print('..v' + app_version_mod + '.ht_api_lib_mapdata')
    mapdata = importlib.import_module('..v' + app_version_mod + '.ht_api_lib_mapdata', 'api.subpkg')
    response['spots'] = mapdata.spot_query_active(body)
    response['spot_requests'] = mapdata.spot_request_query_active(body)
    response['response'] = 'success'
  return jsonify(response)

# RECALL THE SPOT CONTENT DATA
bp_api_spot_content_query = Blueprint('bp_api_spot_content_query', __name__)
@bp_api_spot_content_query.route('/' + ht_references.route_api_spot_content_query, methods=['POST'])
def api_spot_content_query():
  print("ROUTE: SPOT CONTENT QUERY")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    print(app_version_mod)
    print('..v' + app_version_mod + '.ht_api_lib_mapdata')
    mapdata = importlib.import_module('..v' + app_version_mod + '.ht_api_lib_mapdata', 'api.subpkg')
    response['spot_content'] = mapdata.spot_content_query(body)
    response['response'] = 'success'
  return jsonify(response)

# RECALL THE HAZARD DATA
bp_api_hazard_query_active = Blueprint('bp_api_hazard_query_active', __name__)
@bp_api_hazard_query_active.route('/' + ht_references.route_api_hazard_query_active, methods=['POST'])
def api_hazard_query_active():
  print("ROUTE: API - HAZARD QUERY ACTIVE")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    mapdata = importlib.import_module('..v' + app_version_mod + '.ht_api_lib_mapdata', 'api.subpkg')
    response['hazards'] = mapdata.hazard_query_active(body)
    response['response'] = 'success'
  return jsonify(response)

# RECALL THE SHELTER DATA
bp_api_shelter_query_active = Blueprint('bp_api_shelter_query_active', __name__)
@bp_api_shelter_query_active.route('/' + ht_references.route_api_shelter_query_active, methods=['POST'])
def api_shelter_query_active():
  print("ROUTE: API - SHELTER QUERY ACTIVE")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    mapdata = importlib.import_module('..v' + app_version_mod + '.ht_api_lib_mapdata', 'api.subpkg')
    response['shelters'] = mapdata.shelter_query_active(body)
    response['response'] = 'success'
  return jsonify(response)

# RECALL THE HYDRO DATA
bp_api_hydro_query_active = Blueprint('bp_api_hydro_query_active', __name__)
@bp_api_hydro_query_active.route('/' + ht_references.route_api_hydro_query_active, methods=['POST'])
def api_hydro_query_active():
  print("ROUTE: API - HYDRO QUERY ACTIVE")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    mapdata = importlib.import_module('..v' + app_version_mod + '.ht_api_lib_mapdata', 'api.subpkg')
    response['hydro'] = mapdata.hydro_query_active(body)
    response['response'] = 'success'
  return jsonify(response)

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
  # resource = ht_admin_lib.get_resource_with_credentials(identity_id, login_provider, login_token, 'dynamodb', 'us-east-1')
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

# TEST ENDPOINT
bp_test = Blueprint('bp_test', __name__)
@bp_test.route('/test', methods=['GET'])
def test():
  print("ROUTE: API - TEST API")
  util = importlib.import_module('..' + 'v2_0_0' + '.ht_api_lib_util', 'api.subpkg')
  return 'TEST'
