# Current virtenv: harveyvenv

from flask import Blueprint, Flask, jsonify, redirect, render_template, request, send_file
from flask_assets import Environment
from flask_cors import CORS, cross_origin
from base64 import b64encode
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
# from dynamodb_json import json_util
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
# import ht_utility

# Import APP Blueprints
from app.ht_app_route import bp_test \
  , bp_app_test \
  , bp_app_random_id \
  , bp_app_settings \
  , bp_app_login \
  , bp_app_user_check \
  , bp_app_user_update \
  , bp_app_user_query_active \
  , bp_app_user_connection_query \
  , bp_app_user_connection_put \
  , bp_app_skill_query \
  , bp_app_skill_put \
  , bp_app_structure_query \
  , bp_app_structure_put \
  , bp_app_structure_user_query \
  , bp_app_structure_user_put \
  , bp_app_repair_query \
  , bp_app_repair_put \
  , bp_app_spot_query_active \
  , bp_app_spot_put \
  , bp_app_spot_content_status_update \
  , bp_app_spot_request_put \
  , bp_app_hazard_query_active \
  , bp_app_hazard_put \
  , bp_app_shelter_query_active \
  , bp_app_hydro_query_active

# Import API Blueprints
from api.ht_api_route import bp_api_test \
  , bp_api_app_settings \
  , bp_api_cognito_id \
  , bp_api_image_data \
  , bp_api_skill_query \
  , bp_api_skill_put \
  , bp_api_structure_query \
  , bp_api_structure_user_query \
  , bp_api_repair_query \
  , bp_api_spot_query_active \
  , bp_api_spot_content_query \
  , bp_api_hazard_query_active \
  , bp_api_shelter_query_active \
  , bp_api_hydro_query_active

##### KEEP 'APPLICATION': EB environ settings currently looking for 'application' callable by default
application = Flask(__name__,
            static_url_path='',
            static_folder='static') #, static_url_path='')
application.register_blueprint(bp_test)
application.register_blueprint(bp_app_test)
application.register_blueprint(bp_app_random_id)
application.register_blueprint(bp_app_settings)
application.register_blueprint(bp_app_login)
application.register_blueprint(bp_app_user_check)
application.register_blueprint(bp_app_user_update)
application.register_blueprint(bp_app_user_query_active)
application.register_blueprint(bp_app_user_connection_query)
application.register_blueprint(bp_app_user_connection_put)
application.register_blueprint(bp_app_skill_query)
application.register_blueprint(bp_app_skill_put)
application.register_blueprint(bp_app_structure_query)
application.register_blueprint(bp_app_structure_put)
application.register_blueprint(bp_app_structure_user_query)
application.register_blueprint(bp_app_structure_user_put)
application.register_blueprint(bp_app_repair_query)
application.register_blueprint(bp_app_repair_put)
application.register_blueprint(bp_app_spot_query_active)
application.register_blueprint(bp_app_spot_put)
application.register_blueprint(bp_app_spot_content_status_update)
application.register_blueprint(bp_app_spot_request_put)
application.register_blueprint(bp_app_hazard_query_active)
application.register_blueprint(bp_app_hazard_put)
application.register_blueprint(bp_app_shelter_query_active)
application.register_blueprint(bp_app_hydro_query_active)
application.register_blueprint(bp_api_test)
application.register_blueprint(bp_api_app_settings)
application.register_blueprint(bp_api_cognito_id)
application.register_blueprint(bp_api_image_data)
application.register_blueprint(bp_api_skill_query)
application.register_blueprint(bp_api_skill_put)
application.register_blueprint(bp_api_structure_query)
application.register_blueprint(bp_api_structure_user_query)
application.register_blueprint(bp_api_repair_query)
application.register_blueprint(bp_api_spot_query_active)
application.register_blueprint(bp_api_spot_content_query)
application.register_blueprint(bp_api_hazard_query_active)
application.register_blueprint(bp_api_shelter_query_active)
application.register_blueprint(bp_api_hydro_query_active)
application.config["ASSETS_DEBUG"] = ht_references.app_debug
# CORS(application, resources={r"/*": {"origins": "https://feedslant.com/"}})
# CORS(application, resources=r'/api/*')

bundles = ht_references.bundles
assets = Environment(application)
assets.register(bundles)

@application.before_request
def redirect_to_www():
  # Redirect naked domain requests to www
  urlparts = urlparse(request.url)
  if urlparts.netloc == 'harveytown.org':
    urlparts_list = list(urlparts)
    urlparts_list[1] = 'www.harveytown.org'
    return redirect(urlunparse(urlparts_list), code=301)

@application.route('/')
@application.route('/index')
@application.route('/index.html')
# Return the index page
def root():
  print("ROUTE: ROOT")
  # # Request all active Spots and associated SpotContent
  # logo_settings = ht_references.table_logo_settings.query(
  #   TableName=ht_references.table_logo_settings_name
  #   , IndexName="status-index"
  #   , KeyConditionExpression=Key('status').eq('active')
  # )
  return render_template('index.html', refs=ht_references.refs)

@application.route('/map')
# Return the map page
def map():
  print("ROUTE: MAP")
  timestamp_begin = 0
  # Return all active Spots later than the passed timestamp (begin)
  spots = ht_lib_admin.spot_active(timestamp_begin)
  print(spots)
  return render_template('map.html', refs=ht_references.refs, spots=spots)

@application.route('/tos')
@application.route('/tos.html')
# Return the terms of service page
def tos():
  print("ROUTE: tos")
  return render_template('tos.html', refs=ht_references.refs)

@application.route('/about')
@application.route('/about.html')
# Return the about page
def about():
  print("ROUTE: about")
  return render_template('index.html', refs=ht_references.refs)

@application.route('/privacy')
@application.route('/privacy.html')
# Return the privacy policy page
def privacy():
  print("ROUTE: privacy policy")
  return render_template('privacy.html', refs=ht_references.refs)

##### ADMIN PAGES #####
@application.route('/admin/monitor')
@application.route('/admin/monitor/<int:age>')
def admin_monitor(age=1):
  print("ROUTE: ADMIN - MONITOR")
  # If the age (hours) parameter is not passed, default to 1 hour
  # if age is None:
  #   age = 1
  age_seconds = 60 * 60 * age
  # Query for both active and "on hold" Grabs, join the lists, and sort by time
  print("TIME: " + str(time.time()))
  print("TIME GM: " + str(calendar.timegm(time.gmtime())))
  now = calendar.timegm(time.gmtime())
  spot_content_flagged = ht_lib_admin.spot_content_flagged(now - age_seconds)

  identity_id = "us-east-1:3332d565-36ca-458c-80db-58fe85ef876f" #body['identity_id']
  login_provider = "graph.facebook.com" #body['login_provider']
  login_token = "EAACH6QOvruMBAKZCiPGZBMQpnoLZA77AkITLuEE2SvZAPGB504Bkr71TMAsm6xtZAoCmrCC7ZCkB2mvjI0ffHkTAjJiWAEqGN9gEXKGzOHa8i1EL5xmadbepB5nIfhQRo09HgAwr1cv6yzA7DIgJdXaEw7fl3SrAYZAtHb49rUeOPBFBv3cAm1oxWy1HUUUmJBPcnxPgmpSEhawcSZAN9RfrJL1GsRvOFToZD" #body['login_token']
  resource = ht_lib_admin.get_resource_with_credentials(identity_id, login_provider, login_token, 's3', 'us-east-1')

  spot_content_all = []
  for spot_content in spot_content_flagged:
    print(spot_content['content_id'])
    s3_object = resource.Bucket(ht_references.folder_spot_image).Object(spot_content['content_id'] + '.jpg')
    # s3_object = ht_references.s3.Bucket(ht_references.folder_spot_image).Object(spot_content['content_id'] + '.jpg')
    # print(s3_object.get())
    # image64 = b64encode(s3_object.get()["Body"].read())
    image_object = Image.open(BytesIO(s3_object.get()["Body"].read()))
  #   image64 = b64encode(s3_object.get()["Body"].read())
  #   image = image64.decode('base64')

    for orientation in ExifTags.TAGS.keys():
        print(orientation)
        if ExifTags.TAGS[orientation]=='Orientation':
            break
    exif=dict(image_object._getexif().items())
    print(exif)

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
    # buffer = BytesIO()
    # image64.save(buffer, format="JPEG")
    # image = Image.open(image64.decode('base64'))
    # rotated_image = image.rotate(90, expand=1 )
    # print("ORIENTATION:")
    # if hasattr(image, '_getexif'):
    #   orientation = 0x0112
    #   exif = image._getexif()
    #   print(exif)
    #   if exif is not None:
    #     orientation = exif[orientation]
    #     rotations = {
    #         3: Image.ROTATE_180,
    #         6: Image.ROTATE_270,
    #         8: Image.ROTATE_90
    #     }
    #     if orientation in rotations:
    #         image = image.transpose(rotations[orientation])

    # image = s3_object.get()["Body"].read()
    # img = Image.open(image)
    # imgMod = img.rotate(90)
    spot_content['image'] = image64

    params = {'Bucket': 'harvey-media','Key': spot_content['content_id'] + '.jpg'}
    url = ht_references.s3_client.generate_presigned_url('get_object', Params=params, ExpiresIn=86400, HttpMethod='GET')
    spot_content['image_url'] = url
    print(url)
    spot_content_all.append(spot_content)

  spot_content_sorted = sorted(spot_content_flagged, key=itemgetter('timestamp'), reverse=True)
  return render_template('admin-monitor.html', refs=ht_references.refs, spot_content=spot_content_all)


##### APIs #####
# # ENDPOINT TO PASS ADMIN SPOT CONTENT MODIFICATION COMMANDS
# @application.route('/' + ht_references.route_api_admin_update_spot_content, methods=['POST'])
# def admin_modify():
#   print("ROUTE: ADMIN - UPDATE SPOT CONTENT")
#   print(request.json)
#   print(request.headers)
#   print(request.remote_addr)
#   print(list(request.access_route))
#
#   # Retrieve the POST json parameters
#   user_id = request.json['user_id']
#   content_id = request.json['content_id']
#   status = request.json['status']
#
#   response = 'did not start'
#   # # Ensure the user is an admin
#   # u_type = ht_lib_admin.user_type(user_id)
#   # if u_type == 'admin':
#   #   response = ht_lib_admin.update_spot_content_status(content_id, status)
#   # else:
#   #   response = 'unauthorized'
#
#   response = ht_lib_admin.update_spot_content_status(content_id, status)
#   return response


##### TEMPLATE FUNCTIONS #####
@application.context_processor
def ht_context_processor():

  # NOTE: CAREFUL USING SERVER DATETIME FUNCTIONS - WILL CONVERT TO SERVER LOCAL TIME, NOT CLIENT
  # Convert timestamp to datetime readable
  def convert_timestamp(timestamp):
    # # Subtract 5 hours from the timestamp to convert utc to US East time
    # five_hours = 60 * 60 * 5
    # us_east_timestamp = timestamp - five_hours
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

  # Convert timestamp to date readable
  def convert_timestamp_date(timestamp):
    # # Subtract 5 hours from the timestamp to convert utc to US East time
    # five_hours = 60 * 60 * 5
    # us_east_timestamp = timestamp - five_hours
    return datetime.datetime.fromtimestamp(timestamp).strftime('%b %-d, %Y').upper()

  return dict(convert_timestamp=convert_timestamp, convert_timestamp_date=convert_timestamp_date)


##### ERROR PAGES #####
@application.errorhandler(404)
def error_not_found(e):
  return render_template('404.html', refs=ht_references.refs), 404

@application.errorhandler(403)
def error_forbidden(e):
  return render_template('403.html', refs=ht_references.refs), 403

@application.errorhandler(410)
def error_gone(e):
  return render_template('410.html', refs=ht_references.refs), 410

@application.errorhandler(500)
def error_server_error(e):
  return render_template('500.html', refs=ht_references.refs), 500


##### RUN APPLICATION #####
if __name__ == "__main__":
  application.debug = ht_references.app_debug
  if ht_references.app_stage == 'local':
    application.run(host='0.0.0.0', threaded=True)
  else:
    application.run(host='0.0.0.0')
