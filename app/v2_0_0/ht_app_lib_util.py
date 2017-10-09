
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

# Import Harvey libraries
import ht_references
import ht_lib_admin

def app_settings():
  settings = {
    'skill_list' : ht_references.skill_list
    , 'repair_list' : ht_references.repair_list
  }
  return settings

def app_login(body):
  print("LOGIN")
  print(body)
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  response = {}
  new_user = 0
  # QUERY THE PASSED USER
  # Try to find the user via the cognito id, if it does not exist, try the facebook id
  # if that does exist, add the cognito id to the user database and return the user info
  # If neither exist, get a new random user id and create a new user with the default
  # values passed and return the new userID
  table_user = resource.Table(ht_references.table_user_name)
  user_response = table_user.query(
    TableName=ht_references.table_user_name
    , IndexName=ht_references.table_user_index_cognito_id
    , KeyConditionExpression=Key('cognito_id').eq(body['identity_id'])
  )
  if user_response['Count'] > 0:
    response['result'] = 'success'
    response['new_user'] = new_user
    response['user_id'] = user_response['Items'][0]['user_id']
    response['cognito_id'] = body['identity_id']
    response['facebook_id'] = body['facebook_id']
    response['type'] = user_response['Items'][0]['type']
    response['status'] = user_response['Items'][0]['status']
    response['timestamp'] = user_response['Items'][0]['timestamp']
  else:
    # Try the fb id
    user_response = table_user.query(
      TableName=ht_references.table_user_name
      , IndexName=ht_references.table_user_index_fb_id
      , KeyConditionExpression=Key('facebook_id').eq(body['facebook_id'])
    )
    if user_response['Count'] > 0:
      # The users exists, just without a cognito id - add the cognito id to
      # the database and return the user data
      update_user_response = table_user.put_item(
        TableName=ht_references.table_user_name,
        Item={
          'user_id' : user_response['Items'][0]['user_id']
          , 'cognito_id' : body['identity_id']
          , 'facebook_id' : body['facebook_id']
          , 'type' : user_response['Items'][0]['type']
          , 'status' : user_response['Items'][0]['status']
          , 'timestamp' : user_response['Items'][0]['timestamp']
        }
      )
      if update_user_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        response['result'] = 'success'
        response['new_user'] = new_user
        response['user_id'] = user_response['Items'][0]['user_id']
        response['cognito_id'] = body['identity_id']
        response['facebook_id'] = body['facebook_id']
        response['type'] = user_response['Items'][0]['type']
        response['status'] = user_response['Items'][0]['status']
        response['timestamp'] = user_response['Items'][0]['timestamp']
    else:
      new_user = 1
      # Retrieve a random user id
      random_user_id_quotes = app_random_id('{"request" : "random_user_id"}')
      random_user_id = random_user_id_quotes[1:-1]
      current_time = Decimal(time.time())
      # Save the new random userID, along with the passed facebookID to the user Table
      # Save the new user as not having agreed to the eula and privacy policy (will update when agrees)
      create_user_response = table_user.put_item(
        TableName=ht_references.table_user_name,
        Item={
          'user_id' : random_user_id
          , 'cognito_id' : body['identity_id']
          , 'facebook_id' : body['facebook_id']
          , 'type' : 'user'
          , 'status' : 'eula_privacy_none'
          , 'timestamp' : current_time
        }
      )
      if create_user_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        response['result'] = 'success'
        response['new_user'] = new_user
        response['user_id'] = random_user_id
        response['cognito_id'] = body['identity_id']
        response['facebook_id'] = body['facebook_id']
        response['type'] = 'user'
        response['status'] = 'active'
        response['timestamp'] = current_time
  # Retrieve the app settings
  response['settings'] = app_settings()
  return response

def app_random_id(body):
  random_id = ''
  content = 0

  N = 32
  if body['request'] == 'random_user_id':
    N = 16
  elif body['request'] == 'random_sos_id':
    N = 32
  elif body['request'] == 'random_hazard_id':
    N = 32
  elif body['request'] == 'random_spot_id':
    N = 32
  elif body['request'] == 'random_media_id':
    N = 32
  elif body['request'] == 'random_shelter_id':
    N = 32
  elif body['request'] == 'random_structure_id':
    N = 32
  elif body['request'] == 'random_user_image_id':
    N = 32
  elif body['request'] == 'random_comment_id':
    N = 32
  elif body['request'] == 'random_content_id':
    N = 32
  elif body['request'] == 'random_user_interest_id':
    N = 32
  elif body['request'] == 'random_user_name_number':
    N = 10
    content = 1
  if content == 0:
    random_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
  else:
    random_id = ''.join(random.SystemRandom().choice(string.digits) for _ in range(N))
  return random_id

def user_check_by_fbid(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create a default response
  user_exists = 0
  # Recall the requested User
  table_user = resource.Table(ht_references.table_user_name)
  user_response = table_user.query(
  TableName=ht_references.table_user_name
    , IndexName=ht_references.table_user_index_fb_id
    , KeyConditionExpression=Key('facebook_id').eq(body['facebook_id'])
  )
  # Indicate whether the user already exists
  if len(user_response["Items"]) > 0:
    user_exists = 1

  return user_exists

def user_update(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create a default response
  response = 'failure'
  print('USER UPDATE - CHECK 1')
  # Recall the requested User
  user_data = {}
  table_user = resource.Table(ht_references.table_user_name)
  user_response = table_user.query(
    TableName=ht_references.table_user_name
    , KeyConditionExpression=Key('user_id').eq(body['user_id'])
  )
  if len(user_response['Items']) > 0:
    print('USER UPDATE - CHECK 2')
    user_data = {
      'user_id' : body['user_id']
      , 'facebook_id' : user_response['Items'][0]['facebook_id']
      , 'type' : user_response['Items'][0]['type']
      , 'status' : user_response['Items'][0]['status']
      , 'timestamp' : user_response['Items'][0]['timestamp']
    }

    # Update whatever new values were sent (keep the original timestamp and user_id)
    if 'facebook_id' in body:
      print('USER UPDATE - CHECK 3')
      user_data['facebook_id'] = body['facebook_id']
    if 'type' in body:
      user_data['type'] = body['type']
    if 'status' in body:
      user_data['status'] = body['status']

    # Save the new random userID, along with the passed facebookID to the user Table
    create_user_response = table_user.put_item(
      TableName=ht_references.table_user_name,
      Item=user_data
    )
    if create_user_response['ResponseMetadata']['HTTPStatusCode'] == 200:
      print('USER UPDATE - CHECK 4')
      response = 'success'
    return response

def user_query_active(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create an empty response array
  response = []
  # Retrieve the User data
  table_user = resource.Table(ht_references.table_user_name)
  user_response = table_user.query(
    TableName=ht_references.table_user_name
    , IndexName=ht_references.table_user_index
    , KeyConditionExpression=Key('status').eq('active')
  )
  if len(user_response['Items']) > 0:
    response = user_response['Items']
  return response

def user_connection_query(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create an empty response array
  response = []
  # Retrieve the User data
  table_user_conn = resource.Table(ht_references.table_user_conn_name)
  all_connections = []
  # Retrieve the User Connection data
  conn_response = table_user_conn.query(
    TableName=ht_references.table_user_conn_name
    , IndexName=ht_references.table_user_conn_index
    , KeyConditionExpression=Key('user_id').eq(body['user_id'])
  )
  all_connections = conn_response['Items']
  # Retrieve the reverse User Connection data
  conn_target_response = table_user_conn.query(
    TableName=ht_references.table_user_conn_name
    , IndexName=ht_references.table_user_conn_target_index
    , KeyConditionExpression=Key('target_user_id').eq(body['user_id'])
  )
  all_connections = all_connections + conn_target_response['Items']
  return all_connections

def user_connection_put(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create a default response
  response = 'failure'
  # Save the User Connection data
  table_user_conn = resource.Table(ht_references.table_user_conn_name)
  user_conn_response = table_user_conn.put_item(
    TableName=ht_references.table_user_conn_name,
    Item={
      'user_connection_id' : body['user_id'] + "-" + body['target_user_id']
      , 'user_id' : body['user_id']
      , 'target_user_id' : body['target_user_id']
      , 'connection' : body['connection']
      , 'status' : 'active'
    }
  )
  if user_conn_response['ResponseMetadata']['HTTPStatusCode'] == 200:
    response = 'success'
  return response

def skill_query(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create an empty response array
  response = { 'user_id' : body['user_id'] }
  # Recall the Skill data for the user
  table_skill = resource.Table(ht_references.table_skill_name)
  skill_response = table_skill.query(
    TableName=ht_references.table_skill_name
    , IndexName=ht_references.table_skill_index
    , KeyConditionExpression=Key('user_id').eq(body['user_id'])
  )
  response['skill_levels'] = skill_response['Items']
  response['skill_settings'] = ht_references.skill_list
  return response

def skill_put(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create a default response
  response = {'response' : 'success'}
  results = []
  # The skills will be uploaded in a list of dict objects
  # Skill objects should have the same format as the Skill db setup
  # except for the status entry (should always be active)
  for skill_obj in body['skills']:
    # Create or update the current skill entry with the updated data
    table_skill = resource.Table(ht_references.table_skill_name)
    put_skill_response = table_skill.put_item(
      TableName=ht_references.table_skill_name,
      Item={
        'skill_id' : skill_obj['user_id'] + '-' + skill_obj['skill']
        , 'user_id' : skill_obj['user_id']
        , 'skill' : skill_obj['skill']
        , 'level' : Decimal(skill_obj['level'])
        , 'status' : 'active'
      }
    )
    if put_skill_response['ResponseMetadata']['HTTPStatusCode'] == 200:
      results.append('success')
    else:
      results.append('failure')
      response['response'] = 'failure'
  response['results'] = results
  return response

def structure_query(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create a default response
  response = {'response' : 'failure'}
  # If a structure id was passed, only return the specific structure data, otherwise
  # return all active structure data
  table_structure = resource.Table(ht_references.table_structure_name)
  if 'structure_id' in body:
    # Recall the Structure data
    structure_response = table_structure.query(
      TableName=ht_references.table_structure_name
      , KeyConditionExpression=Key('structure_id').eq(body['structure_id'])
    )
  else:
    # Recall all active Structure data
    structure_response = table_structure.query(
      TableName=ht_references.table_structure_name
      , IndexName=ht_references.table_structure_index
      , KeyConditionExpression=Key('status').eq('active')
    )
  if len(structure_response['Items']) > 0:
    response['result'] = 'success'
  response['structures'] = structure_response['Items']
  return response

def structure_put(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create a default response
  response = {'response' : 'failure'}
  # Create data for the structure table
  structure_data = {
    'structure_id' : body['structure_id']
    , 'timestamp' : Decimal(body['timestamp'])
    , 'lat' : Decimal(body['lat'])
    , 'lng' : Decimal(body['lng'])
    , 'type' : Decimal(body['type'])
    , 'stage' : Decimal(body['stage'])
    , 'status' : 'active'
  }
  # Create or update the current structure entry with the updated data
  table_structure = resource.Table(ht_references.table_structure_name)
  put_structure_response = table_structure.put_item(
    TableName=ht_references.table_structure_name,
    Item=structure_data
  )
  if put_structure_response['ResponseMetadata']['HTTPStatusCode'] == 200:
    response['response'] = 'success'
    # Now add all repair entries for this structure with default stages for each
    for repair in ht_references.repair_list:
      repair_body = {
        'identity_id' : body['identity_id']
        , 'login_provider' : body['login_provider']
        , 'login_token' : body['login_token']
        , 'structure_id' : body['structure_id']
        , 'repair' : repair
        , 'stage' : Decimal(0)
        , 'timestamp' : body['timestamp']
        , 'status' : 'active'
      }
      repair_response = repair_put(repair_body)
      if repair_response['response'] == 'failure':
        response['response'] = 'failure'
  return response

def structure_user_query(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # If a structure id was passed, only return the specific structure data, otherwise
  # return all active structure-user data
  found_structure_users = []
  table_structure_user = resource.Table(ht_references.table_structure_user_name)
  if 'structure_id' in body:
    # Recall the Structure data
    structure_user_response = table_structure_user.query(
      TableName=ht_references.table_structure_user_name
      , IndexName=ht_references.table_structure_user_index_structure
      , KeyConditionExpression=Key('structure_id').eq(body['structure_id'])
    )
    found_structure_users = structure_user_response['Items']
  elif 'user_id' in body:
    # Recall the Structure data
    structure_user_response = table_structure_user.query(
      TableName=ht_references.table_structure_user_name
      , IndexName=ht_references.table_structure_user_index_user
      , KeyConditionExpression=Key('user_id').eq(body['user_id'])
    )
    found_structure_users = structure_user_response['Items']
  return found_structure_users

def structure_user_put(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create a default response
  response = {'response' : 'failure'}
  structure_user_data = {
    'structure_user_id' : body['structure_user_id']
    , 'structure_id' : body['structure_id']
    , 'user_id' : body['user_id']
    , 'timestamp' : Decimal(body['timestamp'])
    , 'status' : 'active'
  }
  # Create or update the current structure-user entry with the updated data
  table_structure_user = resource.Table(ht_references.table_structure_user_name)
  put_structure_user_response = table_structure_user.put_item(
    TableName=ht_references.table_structure_user_name,
    Item=structure_user_data
  )
  if put_structure_user_response['ResponseMetadata']['HTTPStatusCode'] == 200:
    response['response'] = 'success'
  return response

def repair_query(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create a default response
  response = {'response' : 'failure'}
  repairs = []
  # If a structure id was passed, only return the specific structure data, otherwise
  # return all active repairs for the passed structure data
  table_repair = resource.Table(ht_references.table_repair_name)
  table_repair_image = resource.Table(ht_references.table_repair_image_name)
  repair_response = table_repair.query(
    TableName=ht_references.table_repair_name
    , IndexName=ht_references.table_repair_index
    , KeyConditionExpression=Key('structure_id').eq(body['structure_id'])
  )
  for repair in repair_response['Items']:
    repair_image_response = table_repair_image.query(
      TableName=ht_references.table_repair_image_name
      , IndexName=ht_references.table_repair_image_index
      , KeyConditionExpression=Key('repair_id').eq(repair['repair_id'])
    )
    repair_images_active = []
    for repair_image in repair_image_response['Items']:
      if repair_image['status'] == 'active':
        repair_images_active.append(repair_image)
    repair['repair_images'] = repair_images_active
    repairs.append(repair)
  # if len(repair_response['Items']) > 0:
  response['result'] = 'success'
  response['repairs'] = repairs
  return response

def repair_put(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create a default response
  response = {'response' : 'failure'}
  # Pull the existing repair - the original timestamp is needed to overwrite original
  table_repair = resource.Table(ht_references.table_repair_name)
  original_timestamp = Decimal(body['timestamp'])
  repair_response = table_repair.query(
    TableName=ht_references.table_repair_name
    , KeyConditionExpression=Key('repair_id').eq(body['structure_id'] + "-" + body['repair'])
  )
  if len(repair_response['Items']) > 0:
    original_timestamp = repair_response['Items'][0]['timestamp']
  repair_data = {
    'repair_id' : body['structure_id'] + "-" + body['repair']
    , 'structure_id' : body['structure_id']
    , 'repair' : body['repair']
    , 'stage' : Decimal(body['stage'])
    , 'timestamp' : original_timestamp
    , 'status' : body['status']
  }
  # Create or update the repair entry with the updated data
  put_repair_response = table_repair.put_item(
    TableName=ht_references.table_repair_name,
    Item=repair_data
  )
  # If new repair images are uploaded, change all old images to inactive
  repair_image_response = 'success'
  if body['updated_images'] == 1:
    # First change all active repair images to inactive
    table_repair_image = resource.Table(ht_references.table_repair_image_name)
    repair_response = table_repair_image.query(
      TableName=ht_references.table_repair_image_name
      , IndexName=ht_references.table_repair_image_index
    #   , KeyConditionExpression=Key('status').eq('active')
      , KeyConditionExpression=Key('repair_id').eq(body['structure_id'] + "-" + body['repair'])
    )
    for repair_image in repair_response['Items']:
      if repair_image['status'] == 'active':
        repair_image_data = {
          'image_id' : repair_image['image_id']
          , 'repair_id' : repair_image['repair_id']
          , 'timestamp' : Decimal(repair_image['timestamp'])
          , 'status' : 'inactive'
        }
        put_repair_image_response = table_repair_image.put_item(
          TableName=ht_references.table_repair_image_name,
          Item=repair_image_data
        )
        if put_repair_image_response['ResponseMetadata']['HTTPStatusCode'] != 200:
          repair_image_response = 'failure'

    # Loop through the updated / new repair images and add the data to the RepairImage db
    for repair_image in body['repair_images']:
      repair_image_data = {
        'image_id' : repair_image['image_id']
        , 'repair_id' : repair_image['repair_id']
        , 'timestamp' : Decimal(repair_image['timestamp'])
        , 'status' : repair_image['status']
      }
      put_repair_image_response = table_repair_image.put_item(
        TableName=ht_references.table_repair_image_name,
        Item=repair_image_data
      )
      if put_repair_image_response['ResponseMetadata']['HTTPStatusCode'] != 200:
        repair_image_response = 'failure'
        print(repair_image_response)
  if put_repair_response['ResponseMetadata']['HTTPStatusCode'] == 200 and repair_image_response == 'success':
    response['response'] = 'success'
  print(response)
  return response
