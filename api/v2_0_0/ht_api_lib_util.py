from flask import Blueprint, Flask, jsonify, redirect, render_template, request, send_file
from flask_assets import Environment
from flask_cors import CORS, cross_origin
from base64 import b64encode
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
from operator import itemgetter
from io import BytesIO
from PIL import Image, ExifTags
from urlparse import urlparse, urlunparse
import boto3
import calendar
import datetime
import decimal
import json
import random
import string
import time
import urllib2

# Import Harvey libraries
import ht_references
import ht_lib_admin

def api_settings():
  settings = {
    'skill_list' : ht_references.skill_list
    , 'repair_types' : ht_references.repair_types
  }
  return settings

def cognito_id(body):
  # Create an empty response json
  response = {}
  cognito_response = ht_references.cognito.get_id(
    AccountId='954817893489'
    , IdentityPoolId=ht_references.cognito_identity_pool_id
    , Logins={
      'graph.facebook.com': body['token']
    }
  )
  # Get the user data based on the fbid
  # Retrieve the User data
  table_user = ht_references.dynamo.Table(ht_references.table_user_name)
  user_response = table_user.query(
    TableName=ht_references.table_user_name
    , IndexName=ht_references.table_user_index_fb_id
    , KeyConditionExpression=Key('facebook_id').eq(body['fb_id'])
  )
  # RETURN A SINGLE USER - NOT A LIST
  if len(user_response['Items']) > 0:
    response = user_response['Items'][0]
  # Now add the cognito identity id as part of the user data
  response['cognito_id'] = cognito_response['IdentityId']
  return response

def image_data(body):
  print("IMAGE DATA:")
  print(body)
  s3_object = ht_references.s3.Bucket(ht_references.folder_spot_image).Object(body['image_key'] + '.jpg')
  image_object = Image.open(BytesIO(s3_object.get()["Body"].read()))

  for orientation in ExifTags.TAGS.keys():
      if ExifTags.TAGS[orientation]=='Orientation':
          break
  exif = dict()
  imgExif = image_object._getexif()
  if imgExif is not None:
      exif=dict(image_object._getexif().items())

      if orientation in exif:
          if exif[orientation] == 3:
              image_object=image_object.rotate(180, expand=True)
          elif exif[orientation] == 6:
              image_object=image_object.rotate(270, expand=True)
          elif exif[orientation] == 8:
              image_object=image_object.rotate(90, expand=True)
#   image64 = b64encode(image_object)
  image_buffer = BytesIO()
  image_object.save(image_buffer, format="JPEG")
  image64 = b64encode(image_buffer.getvalue())

  response = {}
  response['image'] = image64

  params = {'Bucket': 'harvey-media','Key': body['image_key'] + '.jpg'}
  url = ht_references.s3_client.generate_presigned_url('get_object', Params=params, ExpiresIn=86400, HttpMethod='GET')
  response['image_url'] = url
  print(response)
  return response

def user_query_active(body):
  # Create an empty response array
  response = []
  # Retrieve the User data
  table_user = ht_references.dynamo.Table(ht_references.table_user_name)
  user_response = table_user.query(
    TableName=ht_references.table_user_name
    , IndexName=ht_references.table_user_index
    , KeyConditionExpression=Key('status').eq('active')
  )
  # if len(user_response['Items']) > 0:
  #   response = user_response['Items']
  for user in user_response['Items']:
    # fb_profile_response = urllib2.urlopen('https://www.facebook.com/app_scoped_user_id/' + user['facebook_id'])
    # print("USER GET URL:")
    # print(fb_profile_response.geturl())
    response.append(user)
  return response

# Return data for the passed user
def user_query(user_id):
  # Create an empty response array
  response = []
  # Retrieve the User data
  table_user = ht_references.dynamo.Table(ht_references.table_user_name)
  user_response = table_user.query(
    TableName=ht_references.table_user_name
    , KeyConditionExpression=Key('user_id').eq(user_id)
  )
  # RETURN A SINGLE USER - NOT A LIST
  if len(user_response['Items']) > 0:
    fb_profile_response = urllib2.urlopen('https://www.facebook.com/app_scoped_user_id/' + user_response['Items'][0]['facebook_id'])
    print("USER GET URL:")
    print(fb_profile_response.geturl())
    user_response['Items'][0]['user_fb_url'] = fb_profile_response.geturl()
    response = user_response['Items'][0]
  return response

def user_connection_query(body):
  # Create an empty response array
  response = []
  # Retrieve the User data
  table_user_conn = ht_references.dynamo.Table(ht_references.table_user_conn_name)
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
  response['user_skills'] = skill_response['Items']
  response['skill_levels'] = ht_references.skill_levels
  response['skill_types'] = ht_references.skill_types
  return response

def skill_put(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create a default response
  response = {'response' : 'success'}
  # Create or update the current skill entry with the updated data
  table_skill = resource.Table(ht_references.table_skill_name)
  put_skill_response = table_skill.put_item(
    TableName=ht_references.table_skill_name,
    Item={
      'skill_id' : body['user_id'] + '-' + body['skill']
      , 'user_id' : body['user_id']
      , 'skill' : body['skill']
      , 'level' : Decimal(body['level'])
      , 'status' : 'active'
    }
  )
  if put_skill_response['ResponseMetadata']['HTTPStatusCode'] != 200:
    response['response'] = 'failure'
  return response

def structure_query(body):
  # Create a default response
  response = {'result' : 'failure'}
  # If a structure id was passed, only return the specific structure data, otherwise
  # return all active structure data
  table_structure = ht_references.dynamo.Table(ht_references.table_structure_name)
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
    structure_dict = []
    for structure in structure_response['Items']:
      # Add the structure repairs
      repair_response = repair_query(structure)
      if repair_response['result'] == 'success':
        structure['repairs'] = repair_response['repairs']
      # Add the structure users
      structure_user_body = {
        'structure_id' : structure['structure_id']
      }
      structure_user_response = structure_user_query(structure_user_body)
      if len(structure_user_response) > 0:
        structure['users'] = structure_user_response
        structure_dict.append(structure)
    if len(structure_dict) > 0:
      response['structures'] = structure_dict
    else:
      response['result'] = 'failure'
  return response

def structure_user_query(body):
  # If a structure id was passed, only return the specific structure data, otherwise
  # return all active structure-user data
  found_structure_users = []
  table_structure_user = ht_references.dynamo.Table(ht_references.table_structure_user_name)
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
  else:
    # Recall the Structure data
    structure_user_response = table_structure_user.query(
      TableName=ht_references.table_structure_user_name
      , IndexName=ht_references.table_structure_user_index
      , KeyConditionExpression=Key('status').eq('active')
    )
    found_structure_users = structure_user_response['Items']
  return found_structure_users

def repair_query(structure):
  # Create a default response
  response = {'result' : 'failure'}
  repairs = []
  # If a structure id was passed, only return the specific structure data, otherwise
  # return all active repairs for the passed structure data
  table_repair = ht_references.dynamo.Table(ht_references.table_repair_name)
  table_repair_image = ht_references.dynamo.Table(ht_references.table_repair_image_name)
  repair_response = table_repair.query(
    TableName=ht_references.table_repair_name
    , IndexName=ht_references.table_repair_index
    , KeyConditionExpression=Key('structure_id').eq(structure['structure_id'])
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
