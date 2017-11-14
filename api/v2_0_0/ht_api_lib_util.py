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
    , 'repair_list' : ht_references.repair_list
  }
  return settings

def image_data(body):
  s3_object = ht_references.s3.Bucket(ht_references.folder_spot_image).Object(body['image_key'] + '.jpg')
  image_object = Image.open(BytesIO(s3_object.get()["Body"].read()))

  for orientation in ExifTags.TAGS.keys():
      if ExifTags.TAGS[orientation]=='Orientation':
          break
  exif=dict(image_object._getexif().items())

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
  # Create an empty response array
  response = { 'user_id' : body['user_id'] }
  # Recall the Skill data for the user
  table_skill = ht_references.dynamo.Table(ht_references.table_skill_name)
  skill_response = table_skill.query(
    TableName=ht_references.table_skill_name
    , IndexName=ht_references.table_skill_index
    , KeyConditionExpression=Key('user_id').eq(body['user_id'])
  )
  response['skill_levels'] = skill_response['Items']
  response['skill_settings'] = ht_references.skill_list
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
      structure_user_body = {
        'structure_id' : structure['structure_id']
      }
      structure_user_response = structure_user_query(structure_user_body)
      if len(structure_user_response) == 0:
        response['result'] = 'failure'
      else:
        structure['users'] = structure_user_response
        structure_dict.append(structure)
    response['structures'] = structure_dict
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
  return found_structure_users

def repair_query(structure):
  # Create a default response
  response = {'response' : 'failure'}
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
