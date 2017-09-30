# Feedslant admin page functions
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
import boto3
import calendar
import time

#Import local
import ht_references

# s3 = boto3.resource('s3', region_name='us-east-1')
dynamodb_client = boto3.resource('dynamodb', region_name='us-east-1')
table_user = dynamodb_client.Table(ht_references.table_user_name)
table_spot = dynamodb_client.Table(ht_references.table_spot_name)
table_spot_content = dynamodb_client.Table(ht_references.table_spot_content_name)

# METHOD TO GET CLIENT WITH USER CREDENTIALS USING THE PASSED IDENTITY ID AND LOGIN TOKEN
def get_client_with_credentials(identity_id, login_provider, login_token, resource):
  print("GET CREDENTIALS")
  cred = ht_references.cognito.get_credentials_for_identity(
    IdentityId=identity_id
    , Logins={
      login_provider : login_token
      # 'graph.facebook.com' : ''
    }
  )
  # print('CREDENTIALS:')
  # print(cred)
  client = boto3.client(
    resource
    , aws_access_key_id=cred['Credentials']['AccessKeyId']
    , aws_secret_access_key=cred['Credentials']['SecretKey']
    , aws_session_token=cred['Credentials']['SessionToken']
  )
  # print('CLIENT:')
  # print(client)
  return client

# METHOD TO GET RESOURCE WITH USER CREDENTIALS USING THE PASSED IDENTITY ID AND LOGIN TOKEN
def get_resource_with_credentials(identity_id, login_provider, login_token, resource, region):
  print("GET CREDENTIALS FOR RESOURCE")
  cred = ht_references.cognito.get_credentials_for_identity(
    IdentityId=identity_id
    , Logins={
      login_provider : login_token
      # 'graph.facebook.com' : ''
    }
  )
  # print('CREDENTIALS:')
  # print(cred)
  resource = boto3.resource(
    service_name=resource
    , region_name=region
    , aws_access_key_id=cred['Credentials']['AccessKeyId']
    , aws_secret_access_key=cred['Credentials']['SecretKey']
    , aws_session_token=cred['Credentials']['SessionToken']
  )
  print('RESOURCE:')
  print(resource)
  return resource

# METHOD TO GET SESSION WITH USER CREDENTIALS USING THE PASSED IDENTITY ID AND LOGIN TOKEN
def get_session_with_credentials(identity_id, login_provider, login_token, resource):
  print("GET CREDENTIALS FOR SESSION")
  cred = ht_references.cognito.get_credentials_for_identity(
    IdentityId=identity_id
    , Logins={
      login_provider : login_token
      # 'graph.facebook.com' : ''
    }
  )
  # print('CREDENTIALS:')
  # print(cred)
  session = boto3.session.Session(
    aws_access_key_id=cred['Credentials']['AccessKeyId']
    , aws_secret_access_key=cred['Credentials']['SecretKey']
    , aws_session_token=cred['Credentials']['SessionToken']
  )
  print('SESSION:')
  print(session)
  return session

# Ensure the user is an admin
def user_type(user_id):
  user_response = table_user.query(
    TableName=ht_references.table_user_name
    # , IndexName=ht_references.table_user_index_fb_id
    , KeyConditionExpression=Key('user_id').eq(user_id)
  )
  # If the user was returned, check to ensure it is active, if so, return the user type
  u_type = 'inactive'
  if len(user_response['Items']) > 0:
    if admin_user_response['Items'][0]['status'] == 'active':
      u_type = admin_user_response['Items'][0]['type']
  return u_type

# Return all 'active' Spots later than the passed timestamp
def spot_active(timestamp_begin):
  spots_active = table_spot.query(
    TableName=ht_references.table_spot_name
    , IndexName=ht_references.table_spot_index
    , KeyConditionExpression=Key('status').eq('active') & Key('timestamp').gt(Decimal(timestamp_begin))
  )
  return spots_active['Items']

# Return all 'active' SpotContent later than the passed timestamp
def spot_content_active(timestamp_begin):
  spot_content_active = table_spot_content.query(
    TableName=ht_references.table_spot_content_name
    , IndexName=ht_references.table_spot_content_index_status
    , KeyConditionExpression=Key('status').eq('active') & Key('timestamp').gt(Decimal(timestamp_begin))
  )
  return spot_content_active['Items']

# Return the requested SpotContent Object
def spot_content_by_id(content_id):
  spot_content = table_spot_content.query(
    TableName=ht_references.table_spot_content_name
    , IndexName=ht_references.table_spot_content_index_content_id
    , KeyConditionExpression=Key('content_id').eq(content_id)
  )
  return spot_content['Items']

# Return all 'flagged' SpotContent later than the passed timestamp
def spot_content_flagged(timestamp_begin):
  status_strings = ['flagged', 'flag-00', 'flag-01']
  flagged_content = []
  for status in status_strings:
      spot_content_flagged = table_spot_content.query(
        TableName=ht_references.table_spot_content_name
        , IndexName=ht_references.table_spot_content_index_status
        , KeyConditionExpression=Key('status').eq(status) & Key('timestamp').gt(Decimal(timestamp_begin))
      )
      flagged_content += spot_content_flagged['Items']

  return flagged_content

# Update a Spot Content in the db
def update_spot_content_status(content_id, status):
  # Query for the Spot Content to include all other needed info
  for spot_content in spot_content_by_id(content_id):
      if spot_content['content_id'] == content_id:
        # Update the SpotContent object
        response = 'failure'
        spot_content_response = table_spot_content.put_item(
          TableName=ht_references.table_spot_content_name,
          Item={
            'content_id' : content_id
            , 'spot_id' : spot_content['spot_id']
            , 'timestamp' : Decimal(spot_content['timestamp'])
            , 'type' : int(spot_content['type'])
            , 'lat' : Decimal(spot_content['lat'])
            , 'lng' : Decimal(spot_content['lng'])
            , 'status' : status
          }
        )
        if spot_content_response['ResponseMetadata']['HTTPStatusCode'] == 200:
          response = 'success'
  return response
