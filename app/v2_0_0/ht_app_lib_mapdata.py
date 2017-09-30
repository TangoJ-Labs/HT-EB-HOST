
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
import ht_lib_admin


def spot_query_active(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create an empty response array
  response = []
  # Retrieve the Spot data
  table_spot = resource.Table(ht_references.table_spot_name)
  spot_response = table_spot.query(
    TableName=ht_references.table_spot_name
    , IndexName=ht_references.table_spot_index
    , KeyConditionExpression=Key('status').eq('active')
  )
  for spot in spot_response['Items']:
    # Retrieve the Spot Content data
    table_spot_content = resource.Table(ht_references.table_spot_content_name)
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

def spot_put(body):
  from math import sin, cos, sqrt, atan2, radians
  R = 6373.0 # approximate radius of earth in km
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create an empty response array
  responses = []
  # Save the Spot data
  table_spot = resource.Table(ht_references.table_spot_name)
  spot_response = table_spot.put_item(
    TableName=ht_references.table_spot_name,
    Item={
      'spot_id' : body['spot_id']
      , 'user_id' : body['user_id']
      , 'timestamp' : Decimal(body['timestamp'])
      , 'lat' : Decimal(body['lat'])
      , 'lng' : Decimal(body['lng'])
      , 'status' : 'active'
    }
  )
  if spot_response['ResponseMetadata']['HTTPStatusCode'] == 200:
    responses.append('spot_response-success')
  else:
    responses.append('spot_response-failure')
  # Save the Spot Content Data
  spot_content = body['spot_content']
  table_spot_content = resource.Table(ht_references.table_spot_content_name)
  for content in spot_content:
    spot_content_response = table_spot_content.put_item(
      TableName=ht_references.table_spot_content_name,
      Item={
        'content_id' : content['content_id']
        , 'spot_id' : content['spot_id']
        , 'timestamp' : Decimal(content['timestamp'])
        , 'type' : int(content['type'])
        , 'lat' : Decimal(content['lat'])
        , 'lng' : Decimal(content['lng'])
        , 'status' : 'active'
      }
    )
    if spot_content_response['ResponseMetadata']['HTTPStatusCode'] == 200:
      responses.append('spot_content-success')
    else:
      responses.append('spot_content-failure')
  # Convert the Spot coords to radians
  spot_lat_r = radians(Decimal(event['lat']))
  spot_lng_r = radians(Decimal(event['lng']))
  # Check all current requests to see if the current Spot fulfills any
  # Retrieve the SpotRequest data
  table_spot_request = resource.Table(ht_references.table_spot_request_name)
  spot_request_response = table_spot_request.query(
    TableName=ht_references.table_spot_request_name
    , IndexName=ht_references.table_spot_request_index
    , KeyConditionExpression=Key('status').eq('active')
  )
  for spot_request in spot_request_response['Items']:
    spot_req_lat_r = radians(spot_request['lat'])
    spot_req_lng_r = radians(spot_request['lng'])
    c_dist = coord_dist(spot_lat_r, spot_lng_r, spot_req_lat_r, spot_req_lng_r)
    print(c_dist)
    # Distance criteria should match app Spot circle radius (converted to km)
    if c_dist <= 0.05:
      # Change the SpotRequest status to 'filled'
      spot_request_response = table_spot_request.put_item(
        TableName=ht_references.table_spot_request_name,
        Item={
          'request_id' : spot_request['request_id']
          , 'user_id' : spot_request['user_id']
          , 'timestamp' : spot_request['timestamp']
          , 'lat' : spot_request['lat']
          , 'lng' : spot_request['lng']
          , 'status' : 'filled'
        }
      )
      if spot_content_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        responses.append('spot_request-success')
      else:
        responses.append('spot_request-failure')
  return responses

def spot_content_status_update(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create an empty response array
  response = 'failure'
  # Update the Spot Content status
  table_spot_content = resource.Table(ht_references.table_spot_content_name)
  spot_content_response = table_spot_content.query(
    TableName=ht_references.table_spot_content_name
    , IndexName=ht_references.table_spot_content_index_content_id
    , KeyConditionExpression=Key('content_id').eq(body['content_id'])
  )
  if len(spot_content_response['Items']) > 0:
    spot_content = spot_content_response['Items'][0]
    # Save the updated Spot Content Data
    spot_content_response = table_spot_content.put_item(
      TableName=ht_references.table_spot_content_name,
      Item={
        'content_id' : body['content_id']
        , 'spot_id' : spot_content['spot_id']
        , 'timestamp' : Decimal(spot_content['timestamp'])
        , 'type' : int(spot_content['type'])
        , 'lat' : Decimal(spot_content['lat'])
        , 'lng' : Decimal(spot_content['lng'])
        , 'status' : body['status_update']
      }
    )
    if spot_content_response['ResponseMetadata']['HTTPStatusCode'] == 200:
      response = 'success'
  return response

def spot_request_query_active(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create an empty response array
  response = []
  # Retrieve the Spot data
  table_spot_request = resource.Table(ht_references.table_spot_request_name)
  spot_request_response = table_spot_request.query(
    TableName=ht_references.table_spot_request_name
    , IndexName=ht_references.table_spot_request_index
    , KeyConditionExpression=Key('status').eq('active')
  )
  if len(spot_request_response['Items']) > 0:
    response = spot_request_response['Items']
  return response

def spot_request_put(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create an empty response array
  response = 'failure'
  # Retrieve the Spot data
  table_spot_request = resource.Table(ht_references.table_spot_request_name)
  spot_request_response = table_spot_request.put_item(
    TableName=ht_references.table_spot_request_name,
    Item={
      'request_id' : body['request_id']
      , 'user_id' : body['user_id']
      , 'timestamp' : Decimal(body['timestamp'])
      , 'lat' : Decimal(body['lat'])
      , 'lng' : Decimal(body['lng'])
      , 'status' : body['status']
    }
  )
  if spot_request_response['ResponseMetadata']['HTTPStatusCode'] == 200:
    response = 'success'
  return response

def hazard_query_active(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create an empty response array
  response = []
  # Retrieve the Hazard data
  table_hazard = resource.Table(ht_references.table_hazard_name)
  hazard_response = table_hazard.query(
    TableName=ht_references.table_hazard_name
    , IndexName=ht_references.table_hazard_index
    , KeyConditionExpression=Key('status').eq('active')
  )
  if len(hazard_response['Items']) > 0:
    response = hazard_response['Items']
  return response

def hazard_put(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create an empty response array
  response = 'failure'
  # Save the Hazard data
  table_hazard = resource.Table(ht_references.table_hazard_name)
  hazard_response = table_hazard.put_item(
  TableName=ht_references.table_hazard_name,
    Item={
      'hazard_id' : body['hazard_id']
      , 'user_id' : body['user_id']
      , 'timestamp' : Decimal(body['timestamp'])
      , 'lat' : Decimal(body['lat'])
      , 'lng' : Decimal(body['lng'])
      , 'type' : int(body['type'])
      , 'status' : body['status']
    }
  )
  if hazard_response['ResponseMetadata']['HTTPStatusCode'] == 200:
    response = 'success'
  return response

def shelter_query_active(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create an empty response array
  response = []
  # Retrieve the Shelter data
  table_shelter = resource.Table(ht_references.table_shelter_name)
  shelter_response = table_shelter.query(
    TableName=ht_references.table_shelter_name
    , IndexName=ht_references.table_shelter_index
    , KeyConditionExpression=Key('status').eq('active')
  )
  if len(shelter_response['Items']) > 0:
    response = shelter_response['Items']
  return response

def hydro_query_active(body):
  # Create the boto3 resource object with the passed credentials
  resource = ht_lib_admin.get_resource_with_credentials(body['identity_id'], body['login_provider'], body['login_token'], 'dynamodb', 'us-east-1')
  # Create an empty response array
  response = []
  for gauge_id in ht_references.gauge_ids:
    # Retrieve the Hydrologic data
    table_hydro = resource.Table(ht_references.table_hydrologic_name)
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
