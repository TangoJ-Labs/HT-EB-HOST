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
import importlib
import random
import string
import time

# Import local
import ht_references
import ht_lib_admin


# RECALL THE APP SETTINGS
bp_app_settings = Blueprint('bp_app_settings', __name__)
@bp_app_settings.route('/app/settings', methods=['POST'])
def app_settings():
  print("ROUTE: SETTINGS")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    # Replace the periods in the version name to underscores (to match the package name)
    app_version_mod = body['app_version'].replace('.', '_')
    # import the module needed from the package that matches the version name
    util = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_util', 'app.subpkg')
    response['settings'] = util.app_settings()
    response['response'] = 'success'
  return jsonify(response)

# LOG IN A USER
bp_app_login = Blueprint('bp_app_login', __name__)
@bp_app_login.route('/app/login', methods=['POST'])
def app_login():
  print("ROUTE: LOGIN")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    # Replace the periods in the version name to underscores (to match the package name)
    app_version_mod = body['app_version'].replace('.', '_')
    # import the module needed from the package that matches the version name
    util = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_util', 'app.subpkg')
    login_result = util.app_login(body)
    response['login_data'] = login_result
    if login_result['result'] == 'success':
      response['response'] = 'success'
  return jsonify(response)

# CREATE A RANDOM ID
bp_app_random_id = Blueprint('bp_app_random_id', __name__)
@bp_app_random_id.route('/app/randomid', methods=['POST'])
def app_random_id():
  print("ROUTE: RANDOM ID")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    # Replace the periods in the version name to underscores (to match the package name)
    app_version_mod = body['app_version'].replace('.', '_')
    # import the module needed from the package that matches the version name
    util = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_util', 'app.subpkg')
    response['random_id'] = util.app_random_id(body)
    response['response'] = 'success'
  return jsonify(response)

# CHECK A USER EXISTENCE
bp_app_user_check = Blueprint('bp_app_user_check', __name__)
@bp_app_user_check.route('/app/user/check', methods=['POST'])
def app_user_check():
  print("ROUTE: USER CHECK")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    util = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_util', 'app.subpkg')
    response['user_exists'] = util.user_check_by_fbid(body)
    response['response'] = 'success'
  return jsonify(response)

# UPDATE A USER DATA
bp_app_user_update = Blueprint('bp_app_user_update', __name__)
@bp_app_user_update.route('/app/user/update', methods=['POST'])
def app_user_update():
  print("ROUTE: USER UPDATE")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    util = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_util', 'app.subpkg')
    if util.user_update(body) == 'success':
      response['response'] = 'success'
  return jsonify(response)

# RETURN ALL ACTIVE USERS
bp_app_user_query_active = Blueprint('bp_app_user_query_active', __name__)
@bp_app_user_query_active.route('/app/user/query/active', methods=['POST'])
def app_user_query_active():
  print("ROUTE: USER QUERY ACTIVE")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    util = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_util', 'app.subpkg')
    response['users'] = util.user_query_active(body)
    response['response'] = 'success'
  return jsonify(response)

# RETURN ALL USER CONNECTIONS FOR THE PASSED USER
bp_app_user_connection_query = Blueprint('bp_app_user_connection_query', __name__)
@bp_app_user_connection_query.route('/app/user/connection/query', methods=['POST'])
def app_user_connection_query():
  print("ROUTE: USER CONNECTION QUERY")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    util = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_util', 'app.subpkg')
    response['user_connections'] = util.user_connection_query(body)
    response['response'] = 'success'
  return jsonify(response)

# UPDATE / PUT A USER CONNECTION
bp_app_user_connection_put = Blueprint('bp_app_user_connection_put', __name__)
@bp_app_user_connection_put.route('/app/user/connection/put', methods=['POST'])
def app_user_connection_put():
  print("ROUTE: USER CONNECTION PUT")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    util = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_util', 'app.subpkg')
    if util.user_connection_put(body) == 'success':
      response['response'] = 'success'
  return jsonify(response)

# RETURN ALL SKILLS FOR THE PASSED USER
bp_app_skill_query = Blueprint('bp_app_skill_query', __name__)
@bp_app_skill_query.route('/app/skill/query', methods=['POST'])
def app_skill_query():
  print("ROUTE: SKILL QUERY")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    util = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_util', 'app.subpkg')
    response['skills'] = util.skill_query(body)
    response['response'] = 'success'
  return jsonify(response)

# UPDATE / PUT A USER SKILL
bp_app_skill_put = Blueprint('bp_app_skill_put', __name__)
@bp_app_skill_put.route('/app/skill/put', methods=['POST'])
def app_skill_put():
  print("ROUTE: SKILL PUT")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    util = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_util', 'app.subpkg')
    skill_put_response = util.skill_put(body)
    if skill_put_response['response'] == 'success':
      response['response'] = 'success'
  return jsonify(response)

# RETURN ALL STRUCTURES FOR THE PASSED USER
bp_app_structure_query = Blueprint('bp_app_structure_query', __name__)
@bp_app_structure_query.route('/app/structure/query', methods=['POST'])
def app_structure_query():
  print("ROUTE: STRUCTURE QUERY")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    util = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_util', 'app.subpkg')
    query_response = util.structure_query(body)
    if query_response['result'] == 'success':
      response['structures'] = query_response['structures']
      response['repair_settings'] = ht_references.repair_settings
      response['response'] = 'success'
  return jsonify(response)

# UPDATE / PUT A STRUCTURE
bp_app_structure_put = Blueprint('bp_app_structure_put', __name__)
@bp_app_structure_put.route('/app/structure/put', methods=['POST'])
def app_structure_put():
  print("ROUTE: STRUCTURE PUT")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    util = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_util', 'app.subpkg')
    structure_put_response = util.structure_put(body)
    if structure_put_response['response'] == 'success':
      response['response'] = 'success'
  return jsonify(response)

# DELETE A STRUCTURE
bp_app_structure_delete = Blueprint('bp_app_structure_delete', __name__)
@bp_app_structure_delete.route('/app/structure/delete', methods=['POST'])
def app_structure_delete():
  print("ROUTE: STRUCTURE DELETE")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    util = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_util', 'app.subpkg')
    structure_delete_response = util.structure_delete(body)
    if structure_delete_response['response'] == 'success':
      response['response'] = 'success'
  return jsonify(response)

# RETURN ALL STRUCTURE USERS FOR THE PASSED STRUCTURE OR USER, WHICHEVER WAS PASSED
bp_app_structure_user_query = Blueprint('bp_app_structure_user_query', __name__)
@bp_app_structure_user_query.route('/app/structure-user/query', methods=['POST'])
def app_structure_user_query():
  print("ROUTE: STRUCTURE-USER QUERY")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    util = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_util', 'app.subpkg')
    response['structure_users'] = util.structure_user_query(body)
    response['response'] = 'success'
  return jsonify(response)

# UPDATE / PUT A STRUCTURE-USER
bp_app_structure_user_put = Blueprint('bp_app_structure_user_put', __name__)
@bp_app_structure_user_put.route('/app/structure-user/put', methods=['POST'])
def app_structure_user_put():
  print("ROUTE: STRUCTURE-USER PUT")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    util = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_util', 'app.subpkg')
    structure_user_put_response = util.structure_user_put(body)
    if structure_user_put_response['response'] == 'success':
      response['response'] = 'success'
  return jsonify(response)

# RETURN ALL REPAIRS FOR THE PASSED STRUCTURE ID
bp_app_repair_query = Blueprint('bp_app_repair_query', __name__)
@bp_app_repair_query.route('/app/repair/query', methods=['POST'])
def app_repair_query():
  print("ROUTE: REPAIR QUERY")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    util = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_util', 'app.subpkg')
    query_response = util.repair_query(body)
    if query_response['result'] == 'success':
      response['repairs'] = query_response['repairs']
      response['repair_settings'] = ht_references.repair_settings
      response['response'] = 'success'
  return jsonify(response)

# UPDATE / PUT A REPAIR
bp_app_repair_put = Blueprint('bp_app_repair_put', __name__)
@bp_app_repair_put.route('/app/repair/put', methods=['POST'])
def app_repair_put():
  print("ROUTE: REPAIR PUT")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    util = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_util', 'app.subpkg')
    structure_user_put_response = util.repair_put(body)
    if structure_user_put_response['response'] == 'success':
      response['response'] = 'success'
  return jsonify(response)

# RECALL THE SPOT DATA
bp_app_spot_query_active = Blueprint('bp_app_spot_query_active', __name__)
@bp_app_spot_query_active.route('/app/spot/query/active', methods=['POST'])
def app_spot_query_active():
  print("ROUTE: SPOT QUERY ACTIVE")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    mapdata = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_mapdata', 'app.subpkg')
    response['spot'] = mapdata.spot_query_active(body)
    response['spot_request'] = mapdata.spot_request_query_active(body)
    response['response'] = 'success'
  return jsonify(response)

# PUT SPOT DATA
bp_app_spot_put = Blueprint('bp_app_spot_put', __name__)
@bp_app_spot_put.route('/app/spot/put', methods=['POST'])
def app_spot_put():
  print("ROUTE: SPOT PUT")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    mapdata = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_mapdata', 'app.subpkg')
    response['response'] = mapdata.spot_put(body)
  return jsonify(response)

# UPDATE SPOT CONTENT STATUS
bp_app_spot_content_status_update = Blueprint('bp_app_spot_content_status_update', __name__)
@bp_app_spot_content_status_update.route('/app/spot/spotcontent/statusupdate', methods=['POST'])
def app_spot_content_status_update():
  print("ROUTE: SPOT CONTENT STATUS UPDATE")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    mapdata = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_mapdata', 'app.subpkg')
    if mapdata.spot_content_status_update(body) == 'success':
      response['response'] = 'success'
  return jsonify(response)

# PUT SPOT REQUEST DATA
bp_app_spot_request_put = Blueprint('bp_app_spot_request_put', __name__)
@bp_app_spot_request_put.route('/app/spot/spotrequest/put', methods=['POST'])
def app_spot_request_put():
  print("ROUTE: SPOT REQUEST PUT")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    mapdata = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_mapdata', 'app.subpkg')
    if mapdata.spot_request_put(body) == 'success':
      response['response'] = 'success'
  return jsonify(response)

# RECALL THE HAZARD DATA
bp_app_hazard_query_active = Blueprint('bp_app_hazard_query_active', __name__)
@bp_app_hazard_query_active.route('/app/hazard/query/active', methods=['POST'])
def app_hazard_query_active():
  print("ROUTE: HAZARD QUERY ACTIVE")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    mapdata = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_mapdata', 'app.subpkg')
    response['hazard'] = mapdata.hazard_query_active(body)
    response['response'] = 'success'
  return jsonify(response)

# PUT HAZARD DATA
bp_app_hazard_put = Blueprint('bp_app_hazard_put', __name__)
@bp_app_hazard_put.route('/app/hazard/put', methods=['POST'])
def app_hazard_put():
  print("ROUTE: HAZARD PUT")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    mapdata = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_mapdata', 'app.subpkg')
    put_response = mapdata.hazard_put(body)
    if put_response == 'success':
      response['response'] = 'success'
  return jsonify(response)

# RECALL THE SHELTER DATA
bp_app_shelter_query_active = Blueprint('bp_app_shelter_query_active', __name__)
@bp_app_shelter_query_active.route('/app/shelter/query/active', methods=['POST'])
def app_shelter_query_active():
  print("ROUTE: SHELTER QUERY ACTIVE")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    mapdata = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_mapdata', 'app.subpkg')
    response['shelter'] = mapdata.shelter_query_active(body)
    response['response'] = 'success'
  return jsonify(response)

# RECALL THE HYDRO DATA
bp_app_hydro_query_active = Blueprint('bp_app_hydro_query_active', __name__)
@bp_app_hydro_query_active.route('/app/hydro/query/active', methods=['POST'])
def app_hydro_query_active():
  print("ROUTE: HYDRO QUERY ACTIVE")
  # Retrieve the POST json parameters
  body = request.get_json(force=True)
  # Prep the response and fire the appropriate version of the function
  response = {'response' : 'failure'}
  if 'app_version' in body:
    app_version_mod = body['app_version'].replace('.', '_')
    mapdata = importlib.import_module('..v' + app_version_mod + '.ht_app_lib_mapdata', 'app.subpkg')
    response['hydro'] = mapdata.hydro_query_active(body)
    response['response'] = 'success'
  return jsonify(response)

# TEST ENDPOINT - APP
bp_app_test = Blueprint('bp_app_test', __name__)
@bp_app_test.route('/app/test', methods=['GET'])
def app_test():
  print("ROUTE: TEST APP API - MOVED")
  # Retrieve the POST json parameters
  # print(request.get_json(force=True))
  # body = request.get_json(force=True)
  identity_id = "us-east-1:3332d565-36ca-458c-80db-58fe85ef876f" #body['identity_id']
  login_provider = "graph.facebook.com" #body['login_provider']
  login_token = "EAACH6QOvruMBAKZCiPGZBMQpnoLZA77AkITLuEE2SvZAPGB504Bkr71TMAsm6xtZAoCmrCC7ZCkB2mvjI0ffHkTAjJiWAEqGN9gEXKGzOHa8i1EL5xmadbepB5nIfhQRo09HgAwr1cv6yzA7DIgJdXaEw7fl3SrAYZAtHb49rUeOPBFBv3cAm1oxWy1HUUUmJBPcnxPgmpSEhawcSZAN9RfrJL1GsRvOFToZD" #body['login_token']
  # session = ht_lib_admin.get_session_with_credentials(identity_id, login_provider, login_token, 'dynamodb')
  resource = ht_lib_admin.get_resource_with_credentials(identity_id, login_provider, login_token, 'dynamodb', 'us-east-1')
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
  print("ROUTE: TEST API")
  util = importlib.import_module('..' + 'v2_0_0' + '.ht_app_lib_util', 'app.subpkg')
  return 'TEST'
