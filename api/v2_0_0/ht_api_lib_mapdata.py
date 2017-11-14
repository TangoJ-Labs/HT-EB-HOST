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

# Import local
import ht_references
import ht_lib_admin


def spot_query_active(body):
  # Create an empty response array
  response = []
  # Retrieve the Spot data
  table_spot = ht_references.dynamo.Table(ht_references.table_spot_name)
  spot_response = table_spot.query(
    TableName=ht_references.table_spot_name
    , IndexName=ht_references.table_spot_index
    , KeyConditionExpression=Key('status').eq('active')
  )
  for spot in spot_response['Items']:
    # Retrieve the Spot Content data
    table_spot_content = ht_references.dynamo.Table(ht_references.table_spot_content_name)
    spot_content_response = table_spot_content.query(
      TableName=ht_references.table_spot_content_name
      , IndexName=ht_references.table_spot_content_index_spot_id
      , KeyConditionExpression=Key('spot_id').eq(spot['spot_id'])
    )
    # Only add the SpotContent that is 'active'
    spot_content_list = []
    for spot_content in spot_content_response['Items']:
      if spot_content['status'] == 'active':
        spot_content_list.append(spot_content)
    spot['spot_content'] = spot_content_list
    # Only add the Spot if the SpotContent list contains at least one SpotContent (all could have been deactivated)
    if len(spot_content_list) > 0:
      response.append(spot)
  return response

def spot_content_query(body):
  print(body)
  print('SPOT CONTENT QUERY FOR SPOT:')
  print(body['spot_id'])
  # Retrieve the Spot Content data for the passed Spot
  table_spot_content = ht_references.dynamo.Table(ht_references.table_spot_content_name)
  spot_content_response = table_spot_content.query(
    TableName=ht_references.table_spot_content_name
    , IndexName=ht_references.table_spot_content_index_spot_id
    , KeyConditionExpression=Key('spot_id').eq(body['spot_id'])
  )
  # Only add the SpotContent that is 'active'
  spot_content_list = []
  for spot_content in spot_content_response['Items']:
    if spot_content['status'] == 'active':
    #   # Add the temporary url for the Spot Content image
    #   params = {'Bucket': 'harvey-media','Key': spot_content['content_id'] + '.jpg'}
    #   url = ht_references.s3_client.generate_presigned_url('get_object', Params=params, ExpiresIn=86400, HttpMethod='GET')
    #   spot_content['image_url'] = url
      s3_object = ht_references.s3.Bucket(ht_references.folder_spot_image).Object(spot_content['content_id'] + '.jpg')
      image_object = Image.open(BytesIO(s3_object.get()["Body"].read()))
    #   image64 = b64encode(s3_object.get()["Body"].read())
    #   image = image64.decode('base64')

      for orientation in ExifTags.TAGS.keys():
        #   print(orientation)
          if ExifTags.TAGS[orientation]=='Orientation':
              break
      exif=dict(image_object._getexif().items())
    #   print(exif)

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

      spot_content['image'] = image64
      spot_content_list.append(spot_content)
  return spot_content_list

def spot_content_image(body):
  url = ht_references.s3.generate_presigned_url('get_object', Params={'Bucket': '','Key': ''}, ExpiresIn=86400)
  return url

def spot_request_query_active(body):
  # Create an empty response array
  response = []
  # Retrieve the Spot data
  table_spot_request = ht_references.dynamo.Table(ht_references.table_spot_request_name)
  spot_request_response = table_spot_request.query(
    TableName=ht_references.table_spot_request_name
    , IndexName=ht_references.table_spot_request_index
    , KeyConditionExpression=Key('status').eq('active')
  )
  if len(spot_request_response['Items']) > 0:
    response = spot_request_response['Items']
  return response

def hazard_query_active(body):
  # Create an empty response array
  response = []
  # Retrieve the Hazard data
  table_hazard = ht_references.dynamo.Table(ht_references.table_hazard_name)
  hazard_response = table_hazard.query(
    TableName=ht_references.table_hazard_name
    , IndexName=ht_references.table_hazard_index
    , KeyConditionExpression=Key('status').eq('active')
  )
  if len(hazard_response['Items']) > 0:
    response = hazard_response['Items']
  return response

def shelter_query_active(body):
  # Create an empty response array
  response = []
  # Retrieve the Shelter data
  table_shelter = ht_references.dynamo.Table(ht_references.table_shelter_name)
  shelter_response = table_shelter.query(
    TableName=ht_references.table_shelter_name
    , IndexName=ht_references.table_shelter_index
    , KeyConditionExpression=Key('status').eq('active')
  )
  if len(shelter_response['Items']) > 0:
    response = shelter_response['Items']
  return response

def hydro_query_active(body):
  # Create an empty response array
  response = []
  for gauge_id in ht_references.gauge_ids:
    # Retrieve the Hydrologic data
    table_hydro = ht_references.dynamo.Table(ht_references.table_hydrologic_name)
    hydro_response = table_hydro.query(
      TableName=ht_references.table_hydrologic_name
      , IndexName=ht_references.table_hydrologic_index
      , KeyConditionExpression=Key('gauge_id').eq(gauge_id) & Key('status').eq('active')
    )
    latest_reading = {}
    latest_timestamp = 0
    for hydro in hydro_response['Items']:
      # print(hydro)
      if hydro['timestamp'] > latest_timestamp and hydro['status'] == 'active':
        latest_timestamp = hydro['timestamp']
        latest_reading = hydro
    response.append(latest_reading)
  return response
