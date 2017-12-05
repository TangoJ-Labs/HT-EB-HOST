# Feedslant references
import boto3
from boto3.dynamodb.conditions import Key, Attr
from flask import Flask, send_from_directory, url_for
from flask_assets import Bundle

app_stage = 'prod' # prod, dev, local

app_state_name = 'prod'
app_debug = False

##### API ENDPOINT ROUTES #####
# Remove the "/" from the beginning of the path
route_api_app_settings = 'api/settings'
route_api_cognito_id = 'api/cognitoid'
route_api_image_data = 'api/image'
route_api_skill_query = 'api/skill/query'
route_api_skill_put = 'api/skill/put'
route_api_structure_query = 'api/structure/query'
route_api_structure_user_query = 'api/structure-user/query'
route_api_repair_query = 'api/repair/query'
route_api_spot_query_active = 'api/spot/query/active'
route_api_spot_content_query = 'api/spot-content/query/active'
route_api_hazard_query_active = 'api/hazard/query/active'
route_api_shelter_query_active = 'api/shelter/query/active'
route_api_hydro_query_active = 'api/hydro/query/active'
route_api_admin_update_spot_content = 'api/v0.1/admin/update/spot_content'
# route_api_admin_logs = 'api/v0.1/admin/logs'

##### ENDPOINT / URL SETTINGS #####
# ENSURE THE NON-API URLs INCLUDE A SLASH AT THE END
domain = 'https://www.harveytown.org/'
# domain = 'http://harvey.us-east-1.elasticbeanstalk.com/'
if app_stage == 'dev':
  app_state_name = 'dev'
  domain = ''
elif app_stage == 'local':
  app_state_name = 'dev'
  app_debug = True
  # domain = 'http://0.0.0.0:5000/'
  # domain = 'http://127.0.0.1:5000/'
  domain = 'http://192.168.1.7:5000/'

# folder_spot_image = 'https://s3.amazonaws.com/harvey-media/'
folder_spot_image = 'harvey-media'
endpoint_cognito_id = domain + route_api_cognito_id
endpoint_image_data = domain + route_api_image_data
endpoint_skill_query = domain + route_api_skill_query
endpoint_skill_put = domain + route_api_skill_put
endpoint_spot_query_active = domain + route_api_spot_query_active
endpoint_spot_content_query = domain + route_api_spot_content_query
endpoint_hazard_query_active = domain + route_api_hazard_query_active
endpoint_structure_query = domain + route_api_structure_query
endpoint_repair_query = domain + route_api_repair_query
endpoint_admin_update_spot_content = domain + route_api_admin_update_spot_content
# endpoint_admin_logs = domain + route_admin_logs

# if app_stage == 'dev' or app_stage == 'local':
#   folder_spot_image = 'https://s3.amazonaws.com/harvey-media/'

##### HTML SETTINGS #####
# Meta Settings
meta_keywords = "Disaster, Emergency, Repair, Flood, Hurricane"
meta_description = "Crowdsourced disaster response."
meta_image = 'Harvey.png' #FB will not scrape new image unless the filename is changed
fb_app_id = ''

# Standard page html
header_text = '''
  <html>\n<head> <title>Harveytown</title> </head>\n<body>'''
footer_text = '</body>\n</html>'


########## AWS SETTINGSS ##########
# Create boto3 object references
s3 = boto3.resource('s3', region_name='us-east-1')
s3_client = boto3.client('s3', region_name='us-east-1')
dynamo = boto3.resource('dynamodb', region_name='us-east-1')
cognito = boto3.client('cognito-identity', region_name='us-east-1')
cognito_identity_pool_id = 'us-east-1:e831ff1a-257a-4363-abe0-ca6ef52a3c0d'

##### LAMBDA FUNCTION SETTINGS #####
function_get_spot_data = 'HT-GetSpotData'
# if app_stage == 'dev' or app_stage == 'local':
#   function_get_spot_data = 'HT-GetSpotData'

##### DYNAMODB TABLE SETTINGS #####
# Logo settings table
table_user_name = 'Harvey-User'
table_user_conn_name = 'Harvey-UserConnection'
table_skill_name = 'Harvey-Skill'
table_structure_name = 'Harvey-Structure'
table_structure_user_name = 'Harvey-StructureUser'
table_repair_name = 'Harvey-Repair'
table_repair_image_name = 'Harvey-RepairImage'
table_spot_name = 'Harvey-Spot'
table_spot_content_name = 'Harvey-SpotContent'
table_spot_request_name = 'Harvey-SpotRequest'
table_hazard_name = 'Harvey-Hazard'
table_shelter_name = 'Harvey-Shelter'
table_hydrologic_name = 'Harvey-Hydrologic'

# if app_stage == 'dev' or app_stage == 'local':
#   table_spot_name = 'Harvey-DEV-Spot'

# Create the Table objects and index settings
table_user_index = 'status-index'
table_user_index_cognito_id = 'cognito_id-index'
table_user_index_fb_id= 'facebook_id-index'
table_user_conn_index = 'user_id-index'
table_user_conn_target_index = 'target_user_id-index'
table_skill_index = 'user_id-index'
table_structure_index = 'status-timestamp-index'
table_structure_user_index_structure = 'structure_id-timestamp-index'
table_structure_user_index_user = 'user_id-timestamp-index'
table_repair_index = 'structure_id-index'
table_repair_image_index = 'repair_id-timestamp-index'
table_repair_image_index_status = 'status-timestamp-index'
table_spot_index = 'status-timestamp-index'
table_spot_content_index_status = 'status-timestamp-index'
table_spot_content_index_spot_id = 'spot_id-timestamp-index'
table_spot_content_index_content_id= 'content_id-timestamp-index'
table_spot_request_index = 'status-timestamp-index'
table_hazard_index = 'status-timestamp-index'
table_shelter_index = 'status-index'
table_hydrologic_index = 'gauge_id-status-index'

skill_types = {
  'mucking' : {'title':'mucking', 'order':1, 'image':'mucking.png'}
  , 'electrical' : {'title':'electrical', 'order':2, 'image':'electrical.png'}
  , 'plumbing' : {'title':'plumbing', 'order':3, 'image':'plumbing.png'}
  , 'framing' : {'title':'framing', 'order':4, 'image':'framing.png'}
  , 'concrete' : {'title':'concrete', 'order':5, 'image':'concrete.png'}
  , 'sheetrock' : {'title':'sheetrock repair', 'order':6, 'image':'sheetrock.png'}
  , 'texturing' : {'title':'texturing', 'order':7, 'image':'texturing.png'}
  , 'painting' : {'title':'painting', 'order':8, 'image':'painting.png'}
  , 'tiling' : {'title':'tiling', 'order':9, 'image':'tile.png'}
  , 'cabinetry' : {'title':'cabinetry', 'order':10, 'image':'cabinetry.png'}
  , 'roofing' : {'title':'roofing', 'order':11, 'image':'roof.png'}
  , 'fencing' : {'title':'building fences', 'order':12, 'image':'fence.png'}
  , 'windows' : {'title':'installing windows', 'order':13, 'image':'window.png'}
  , 'fixtures' : {'title':'installing fixtures', 'order':14, 'image':'fixture.png'}
  , 'appliances' : {'title':'repairing appliances', 'order':15, 'image':'appliance.png'}
  , 'landscaping' : {'title':'landscaping', 'order':16, 'image':'landscaping.png'}
  # , 'general woodworking' : {'order':17, 'image':'Harvey.png'}
  # , 'heavy lifting' : {'order':18, 'image':'Harvey.png'}
}
skill_levels = {
  0 : {'title':'No Experience', 'color':'#CCCCCC'}
  , 1 : {'title':'Some Experience', 'color':'#F9A01E'}
  , 2 : {'title':'Expert', 'color':'#44A9DF'}
}
repair_types = {
  'mucking' : {'title':'mucking', 'order':1, 'image':'mucking.png'
               , 'skills': ['mucking']}
  , 'electrical' : {'title':'electrical replacement', 'order':2, 'image':'electrical.png'
               , 'skills': ['electrical']}
  , 'plumbing' : {'title':'plumbing patching', 'order':3, 'image':'plumbing.png'
               , 'skills': ['plumbing']}
  , 'framing' : {'title':'framing repair', 'order':4, 'image':'framing.png'
               , 'skills': ['framing']}
  , 'concrete' : {'title':'concrete patching', 'order':5, 'image':'concrete.png'
               , 'skills': ['concrete']}
  , 'sheetrock01' : {'title':'sheetrock repair', 'order':6, 'image':'sheetrock.png'
               , 'skills': ['sheetrock']}
  , 'sheetrock02' : {'title':'sheetrock texturing', 'order':7, 'image':'texturing.png'
               , 'skills': ['texturing']}
  , 'painting01' : {'title':'interior painting', 'order':8, 'image':'painting.png'
               , 'skills': ['painting']}
  , 'tile' : {'title':'tile laying', 'order':9, 'image':'tile.png'
               , 'skills': ['tiling']}
  , 'cabinets' : {'title':'cabinet installation', 'order':10, 'image':'cabinetry.png'
               , 'skills': ['cabinetry']}
  , 'roof' : {'title':'roof repair', 'order':11, 'image':'roof.png'
               , 'skills': ['roofing']}
  , 'fence' : {'title':'fence construction', 'order':12, 'image':'fence.png'
               , 'skills': ['fencing']}
  , 'window' : {'title':'window installation', 'order':13, 'image':'window.png'
               , 'skills': ['windows']}
  , 'painting02' : {'title':'exterior painting', 'order':14, 'image':'painting.png'
               , 'skills': ['painting']}
  , 'fixture' : {'title':'fixture installation', 'order':15, 'image':'fixture.png'
               , 'skills': ['fixtures']}
  , 'appliance' : {'title':'appliance repair / install', 'order':16, 'image':'appliance.png'
               , 'skills': ['appliances']}
  , 'landscaping' : {'title':'landscaping', 'order':17, 'image':'landscaping.png'
               , 'skills': ['landscaping']}
}
# REPAIR STAGES ARE HARD-CODED IN THE APP
repair_stages = {
  0 : {'title':'na', 'color':'#FFFFFF'}
  , 1 : {'title':'need help', 'color':'#B34700'}
  , 2 : {'title':'repairing', 'color':'#B38F00'}
  , 3 : {'title':'complete', 'color':'#248F24'}
  , 4 : {'title':'other', 'color':'#1A1A1A'}
}
repair_settings = {
  'types' : repair_types
  , 'stages' : repair_stages
}

# FLASK ASSET BUNDLES FOR REFERENCE & MINIFICATION
bundles = {
    'index_js': Bundle(
        'js/index.js',
        output='gen/index-min.js',
        filters='jsmin'),

    'index_css': Bundle(
        'css/index.css',
        output='gen/index-min.css',
        filters='cssmin'),

    'map_js': Bundle(
        'js/map.js',
        output='gen/map-min.js',
        filters='jsmin'),

    'map_css': Bundle(
        'css/map.css',
        output='gen/map-min.css',
        filters='cssmin'),

    'error_css': Bundle(
        'css/error.css',
        output='gen/error-min.css',
        filters='cssmin'),

    'policy_css': Bundle(
        'css/policy.css',
        output='gen/policy-min.css',
        filters='cssmin'),

    'admin_monitor_js': Bundle(
        'js/admin-monitor.js',
        output='gen/admin-monitor-min.js',
        filters='jsmin'),

    'admin_monitor_css': Bundle(
        'css/admin-monitor.css',
        output='gen/admin-monitor-min.css',
        filters='cssmin'),
}

##### COMPILE THE REFS DICT #####
refs = {'app_stage' : app_stage
  , 'domain' : domain
  , 'folder_spot_image' : folder_spot_image
  , 'endpoint_cognito_id' : endpoint_cognito_id
  , 'endpoint_image_data' : endpoint_image_data
  , 'endpoint_skill_query' : endpoint_skill_query
  , 'endpoint_skill_put' : endpoint_skill_put
  , 'endpoint_spot_query_active' : endpoint_spot_query_active
  , 'endpoint_spot_content_query' : endpoint_spot_content_query
  , 'endpoint_hazard_query_active' : endpoint_hazard_query_active
  , 'endpoint_structure_query' : endpoint_structure_query
  , 'endpoint_repair_query' : endpoint_repair_query
  # , 'endpoint_admin_logs' : endpoint_admin_logs
  , 'endpoint_admin_update_spot_content' : endpoint_admin_update_spot_content
  , 'meta_keywords' : meta_keywords
  , 'meta_description' : meta_description
  , 'meta_image' : meta_image
  , 'fb_app_id' : fb_app_id
}

gauge_ids = [
    'PRBT2'
    , 'ALOT2'
    , 'JSPT2'
    , 'LUFT2'
    , 'SKMT2'
    , 'HAGT2'
    , 'MYAT2'
    , 'WTTT2'
    , 'ATBT2'
    , 'AYIT2'
    , 'SGAT2'
    , 'ABTT2'
    , 'WBRT2'
    , 'BEST2'
    , 'MBCT2'
    , 'ELTT2'
    , 'MDST2'
    , 'GTWT2'
    , 'BCNT2'
    , 'BGKT2'
    , 'JFET2'
    , 'PBGT2'
    , 'BSNT2'
    , 'BGET2'
    , 'BRPT2'
    , 'EGZT2'
    , 'JYMT2'
    , 'JEFT2'
    , 'BAPT2'
    , 'BFST2'
    , 'BRBT2'
    , 'BSMT2'
    , 'KYET2'
    , 'WMBT2'
    , 'TBPT2'
    , 'BRAT2'
    , 'HBMT2'
    , 'AMTT2'
    , 'AQLT2'
    , 'BAWT2'
    , 'BBZT2'
    , 'DNNT2'
    , 'GLRT2'
    , 'HIBT2'
    , 'HPDT2'
    , 'JTBT2'
    , 'LHPT2'
    , 'LSET2'
    , 'PLOT2'
    , 'RMOT2'
    , 'ROST2'
    , 'SOUT2'
    , 'SYMT2'
    , 'WBAT2'
    , 'WCBT2'
    , 'BCIT2'
    , 'BKFT2'
    , 'BSYT2'
    , 'BYBT2'
    , 'ADDT2'
    , 'BAKT2'
    , 'BBST2'
    , 'PPTT2'
    , 'WSBT2'
    , 'STFT2'
    , 'AMAT2'
    , 'CDNT2'
    , 'MRIT2'
    , 'SDAT2'
    , 'HCDT2'
    , 'RCET2'
    , 'CCRT2'
    , 'LCRT2'
    , 'CICT2'
    , 'CNXT2'
    , 'CSVT2'
    , 'FCTT2'
    , 'HDWT2'
    , 'SELT2'
    , 'SUPT2'
    , 'HCCT2'
    , 'SGET2'
    , 'ABYT2'
    , 'HWLT2'
    , 'NGTT2'
    , 'ROYT2'
    , 'FWHT2'
    , 'WEAT2'
    , 'CCVT2'
    , 'CKDT2'
    , 'SCDT2'
    , 'ACRT2'
    , 'ALKT2'
    , 'BACT2'
    , 'BLIT2'
    , 'BRTT2'
    , 'BUDT2'
    , 'CBST2'
    , 'CDCT2'
    , 'GPLT2'
    , 'IKLT2'
    , 'IRAT2'
    , 'JBGT2'
    , 'JBTT2'
    , 'LGRT2'
    , 'MFDT2'
    , 'MRCT2'
    , 'MSDT2'
    , 'RELT2'
    , 'SILT2'
    , 'SMIT2'
    , 'SNBT2'
    , 'STYT2'
    , 'WCHT2'
    , 'WHAT2'
    , 'NBCT2'
    , 'PRKT2'
    , 'SCCT2'
    , 'RCCT2'
    , 'MCVT2'
    , 'PICT2'
    , 'GNVT2'
    , 'CCGT2'
    , 'KHOT2'
    , 'WFDT2'
    , 'LYNT2'
    , 'DEET2'
    , 'DCJT2'
    , 'BKCT2'
    , 'CMKT2'
    , 'JNXT2'
    , 'KNBT2'
    , 'NBDT2'
    , 'CUST2'
    , 'HTWT2'
    , 'CLDT2'
    , 'NCET2'
    , 'CNLT2'
    , 'MCKT2'
    , 'LMCT2'
    , 'DEYT2'
    , 'BAMT2'
    , 'CART2'
    , 'GLLT2'
    , 'WRST2'
    , 'CHOT2'
    , 'CNCT2'
    , 'DBYT2'
    , 'TIDT2'
    , 'UDET2'
    , 'NGCT2'
    , 'GNST2'
    , 'GBHT2'
    , 'GBLT2'
    , 'HGBT2'
    , 'QGCT2'
    , 'COMT2'
    , 'CUET2'
    , 'DUPT2'
    , 'GBCT2'
    , 'GDHT2'
    , 'GNLT2'
    , 'GRTT2'
    , 'GWGT2'
    , 'HNTT2'
    , 'KRRT2'
    , 'NBRT2'
    , 'SEGT2'
    , 'SMCT2'
    , 'SRGT2'
    , 'STLT2'
    , 'TIVT2'
    , 'TVLT2'
    , 'VICT2'
    , 'BABT2'
    , 'CPNT2'
    , 'IRDT2'
    , 'MQTT2'
    , 'PACT2'
    , 'PCNT2'
    , 'RCPT2'
    , 'RTAT2'
    , 'SDRT2'
    , 'TAQT2'
    , 'VCAT2'
    , 'HBRT2'
    , 'CRFT2'
    , 'WFHT2'
    , 'KWHT2'
    , 'ABAT2'
    , 'SFIT2'
    , 'JCIT2'
    , 'GWLT2'
    , 'FCWT2'
    , 'LFKT2'
    , 'QTMT2'
    , 'KEMT2'
    , 'LSPT2'
    , 'EDNT2'
    , 'HTST2'
    , 'HLCT2'
    , 'LECT2'
    , 'LKST2'
    , 'BLET2'
    , 'DLLT2'
    , 'GAST2'
    , 'HMLT2'
    , 'LBFT2'
    , 'JFFT2'
    , 'ORCT2'
    , 'JYLT2'
    , 'CMNT2'
    , 'LRIT2'
    , 'RLRT2'
    , 'ALWT2'
    , 'ARHT2'
    , 'ARRT2'
    , 'HTAT2'
    , 'JNCT2'
    , 'LLAT2'
    , 'MLRT2'
    , 'LIVT2'
    , 'FAFT2'
    , 'HFFT2'
    , 'LMKT2'
    , 'LMTT2'
    , 'HEIT2'
    , 'BMCT2'
    , 'BDAT2'
    , 'MDLT2'
    , 'MERT2'
    , 'MMDT2'
    , 'SAAT2'
    , 'SMMT2'
    , 'MIOT2'
    , 'RYET2'
    , 'MCGT2'
    , 'TKST2'
    , 'TLPT2'
    , 'DMYT2'
    , 'BEMT2'
    , 'SMKT2'
    , 'REFT2'
    , 'CLRT2'
    , 'CMHT2'
    , 'JKST2'
    , 'LMVT2'
    , 'EAST2'
    , 'GRST2'
    , 'NGET2'
    , 'LSNT2'
    , 'MRAT2'
    , 'SBMT2'
    , 'SPAT2'
    , 'ATOT2'
    , 'BEAT2'
    , 'DIBT2'
    , 'EVDT2'
    , 'LPTT2'
    , 'NCST2'
    , 'NSBT2'
    , 'ROKT2'
    , 'TBFT2'
    , 'TBLT2'
    , 'BUMT2'
    , 'CTNT2'
    , 'HICT2'
    , 'VMAT2'
    , 'CLBT2'
    , 'SNCT2'
    , 'SRCT2'
    , 'IPRT2'
    , 'SHAT2'
    , 'JCTT2'
    , 'CPPT2'
    , 'ACTT2'
    , 'ALAT2'
    , 'ATHT2'
    , 'BCAT2'
    , 'BDLT2'
    , 'BDWT2'
    , 'BLBT2'
    , 'BLNT2'
    , 'BNBT2'
    , 'BPRT2'
    , 'BSAT2'
    , 'CCST2'
    , 'DAWT2'
    , 'EAMT2'
    , 'FFLT2'
    , 'FLWT2'
    , 'FRHT2'
    , 'GBYT2'
    , 'GPET2'
    , 'GPVT2'
    , 'GQQT2'
    , 'HCRT2'
    , 'JPLT2'
    , 'LART2'
    , 'LCJT2'
    , 'LCLT2'
    , 'LEWT2'
    , 'LLET2'
    , 'LLST2'
    , 'LMGT2'
    , 'LPPT2'
    , 'LTLT2'
    , 'LVNT2'
    , 'LWFT2'
    , 'LWWT2'
    , 'MFCT2'
    , 'MMWT2'
    , 'MYST2'
    , 'NNCT2'
    , 'PCTT2'
    , 'PNTT2'
    , 'PSMT2'
    , 'RRLT2'
    , 'SCLT2'
    , 'STIT2'
    , 'TRNT2'
    , 'WTYT2'
    , 'PWRT2'
    , 'TRST2'
    , 'ASRT2'
    , 'BTVT2'
    , 'CAAT2'
    , 'CBVT2'
    , 'COTT2'
    , 'GWNT2'
    , 'MTBT2'
    , 'MTHT2'
    , 'THET2'
    , 'TILT2'
    , 'UVAT2'
    , 'UVLT2'
    , 'SIOT2'
    , 'ATIT2'
    , 'DRWT2'
    , 'ONIT2'
    , 'OOST2'
    , 'WEOT2'
    , 'SPMT2'
    , 'SPRT2'
    , 'GROT2'
    , 'SPDT2'
    , 'CDPT2'
    , 'VERT2'
    , 'BWDT2'
    , 'CUTT2'
    , 'LBWT2'
    , 'MLIT2'
    , 'SGOT2'
    , 'BTNT2'
    , 'GIVT2'
    , 'LTRT2'
    , 'ORLT2'
    , 'PCST2'
    , 'PDAT2'
    , 'PGFT2'
    , 'RLAT2'
    , 'SPCT2'
    , 'FRBT2'
    , 'JOCT2'
    , 'PEDT2'
    , 'BIPT2'
    , 'JYKT2'
    , 'JYNT2'
    , 'JZBT2'
    , 'SOLT2'
    , 'PLPT2'
    , 'LULT2'
    , 'BICT2'
    , 'CHLT2'
    , 'WAYT2'
    , 'KLGT2'
    , 'BKBT2'
    , 'DEKT2'
    , 'DSNT2'
    , 'DSTT2'
    , 'GSVT2'
    , 'RBUT2'
    , 'AMIT2'
    , 'BOQT2'
    , 'CBBT2'
    , 'CDBT2'
    , 'CDET2'
    , 'CSTT2'
    , 'DLRT2'
    , 'DYNT2'
    , 'ELNT2'
    , 'EMDT2'
    , 'EPPT2'
    , 'EPRT2'
    , 'FALT2'
    , 'FQGT2'
    , 'LDOT2'
    , 'LNYT2'
    , 'LOBT2'
    , 'LWTT2'
    , 'MADT2'
    , 'MCDT2'
    , 'PIOT2'
    , 'PLXT2'
    , 'PRDT2'
    , 'PRST2'
    , 'RCLT2'
    , 'RGAT2'
    , 'RGDT2'
    , 'SBNT2'
    , 'TELT2'
    , 'TGAT2'
    , 'ZGBT2'
    , 'SHCT2'
    , 'DSBT2'
    , 'SABT2'
    , 'BEKT2'
    , 'BKLT2'
    , 'BRVT2'
    , 'BWRT2'
    , 'DWYT2'
    , 'GDWT2'
    , 'HAKT2'
    , 'LONT2'
    , 'MLAT2'
    , 'ORNT2'
    , 'SACT2'
    , 'SSCT2'
    , 'ARTT2'
    , 'CWRT2'
    , 'PNVT2'
    , 'GRET2'
    , 'WLGT2'
    , 'ELMT2'
    , 'FACT2'
    , 'FLVT2'
    , 'GLIT2'
    , 'MFNT2'
    , 'SNPT2'
    , 'SRRT2'
    , 'BOLT2'
    , 'EBBT2'
    , 'SWYT2'
    , 'FRRT2'
    , 'ACET2'
    , 'AICT2'
    , 'GETT2'
    , 'GGLT2'
    , 'GNGT2'
    , 'SHLT2'
    , 'LLGT2'
    , 'SMRT2'
    , 'SRUT2'
    , 'TNLT2'
    , 'BSST2'
    , 'MNRT2'
    , 'SSBT2'
    , 'SCGT2'
    , 'WHOT2'
    , 'CODT2'
    , 'KNLT2'
    , 'SCRT2'
    , 'HSIT2'
    , 'BVWT2'
    , 'CHVT2'
    , 'QLAT2'
    , 'DSCT2'
    , 'COPT2'
    , 'BENT2'
    , 'BPST2'
    , 'CRTT2'
    , 'HSJT2'
    , 'LCTT2'
    , 'LTXT2'
    , 'LVDT2'
    , 'SOMT2'
    , 'SPNT2'
    , 'TMBT2'
    , 'TKLT2'
    , 'SKCT2'
    , 'NAPT2'
    , 'TLCT2'
    , 'KTNT2'
    , 'TNGT2'
    , 'LCH'
    , 'SBPT2'
    , 'KIVT2'
    , 'MTPT2'
    , 'CRKT2'
    , 'DALT2'
    , 'GRIT2'
    , 'LBYT2'
    , 'LOLT2'
    , 'MBFT2'
    , 'RMYT2'
    , 'RSRT2'
    , 'RVRT2'
    , 'TDDT2'
    , 'MKZT2'
    , 'ERMT2'
    , 'KOUT2'
    , 'MNFT2'
    , 'ABIT2'
    , 'BCRT2'
    , 'BLKT2'
    , 'EVST2'
    , 'HAWT2'
    , 'HORT2'
    , 'KBYT2'
    , 'LKCT2'
    , 'LSFT2'
    , 'LSWT2'
    , 'NAST2'
    , 'OHIT2'
    , 'SAGT2'
    , 'TBRT2'
    , 'CFKT2'
    , 'HMMT2'
    , 'POET2'
    , 'BOYT2'
    , 'FWOT2'
    , 'GPRT2'
    , 'JAKT2'
    , 'GNDT2'
    , 'NUBT2'
    , 'HGTT2'
    , 'WOCT2'
    , 'DWRT2'
    , 'CHWT2'
    , 'DDET2'
    , 'IPWT2'
    , 'MBLT2'
    , 'SEYT2'
    , 'SYOT2'
    , 'WICT2'
    , 'EGYT2'
    , 'LWCT2'
    , 'LCBT2'
    , 'ZACT2'
    , 'LITF1' #FLORIDA START
    , 'RVWF1'
    , 'JNAF1'
    , 'ALQF1'
    , 'ACSF1'
    , 'ELFF1'
    , 'BLOF1'
    , 'CHAF1'
    , 'SMAF1'
    , 'WAHF1'
    , 'WDRF1'
    , 'WWAF1'
    , 'FRDF1'
    , 'ASHF1'
    , 'LAMF1'
    , 'NUTF1'
    , 'BYMF1'
    , 'BEBF1'
    , 'MLNF1'
    , 'BCMF1'
    , 'BLBF1'
    , 'BAKF1'
    , 'BLUF1'
    , 'BLSF1'
    , 'BSDF1'
    , 'BRJF1'
    , 'BREF1'
    , 'BYCF1'
    , 'TRDF1'
    , 'JAKF1'
    , 'ALTF1'
    , 'MALF1'
    , 'SCTF1'
    , 'WWCF1'
    , 'BRUF1'
    , 'CARF1'
    , 'PITF1'
    , 'CCJF1'
    , 'WRGF1'
    , 'SPUF1'
    , 'DPLF1'
    , 'DCDF1'
    , 'DNSF1'
    , 'DUCF1'
    , 'MRTF1'
    , 'BENF1'
    , 'ECBF1'
    , 'ECOF1'
    , 'ELVF1'
    , 'PCLF1'
    , 'CTYF1'
    , 'MNOF1'
    , 'FENF1'
    , 'FLYF1'
    , 'FOLF1'
    , 'SPHF1'
    , 'APCF1'
    , 'CKYF1'
    , 'HSBF1'
    , 'PACF1'
    , 'PCBF1'
    , 'PGBF1'
    , 'SBIF1'
    , 'SHPF1'
    , 'HAMF1'
    , 'RLGF1'
    , 'HACF1'
    , 'FOWF1'
    , 'MORF1'
    , 'ZPHF1'
    , 'VRNF1'
    , 'ARHF1'
    , 'ICSF1'
    , 'BNNF1'
    , 'IRWF1'
    , 'MEIF1'
    , 'PDLF1'
    , 'RDEF1'
    , 'SAIF1'
    , 'JULF1'
    , 'JNPF1'
    , 'LSSF1'
    , 'QCYF1'
    , 'LECF1'
    , 'WIMF1'
    , 'MIDF1'
    , 'LWAF1'
    , 'ARNF1'
    , 'LCRF1'
    , 'LXRF1'
    , 'MKHF1'
    , 'MTDF1'
    , 'RYEF1'
    , 'BINF1'
    , 'MMPF1'
    , 'MKCF1'
    , 'RDDF1'
    , 'NATF1'
    , 'NRBF1'
    , 'SNWF1'
    , 'MDLF1'
    , 'BLXF1'
    , 'CONF1'
    , 'CTMF1'
    , 'HVNF1'
    , 'JBDF1'
    , 'OCLF1'
    , 'CNRF1'
    , 'EURF1'
    , 'MSSF1'
    , 'OKRF1'
    , 'RODF1'
    , 'ONGF1'
    , 'ORKF1'
    , 'PLMF1'
    , 'ARCF1'
    , 'BARF1'
    , 'ZFSF1'
    , 'BRPF1'
    , 'PCUF1'
    , 'PSJF1'
    , 'RABF1'
    , 'RNBF1'
    , 'SSSF1'
    , 'ERLF1'
    , 'FTWF1'
    , 'FWHF1'
    , 'GRMF1'
    , 'HSPF1'
    , 'OLPF1'
    , 'POEF1'
    , 'RRZF1'
    , 'TREF1'
    , 'WORF1'
    , 'SHIF1'
    , 'SNCF1'
    , 'CRVF1'
    , 'MHDF1'
    , 'SOPF1'
    , 'PNYF1'
    , 'SLLF1'
    , 'SLRF1'
    , 'SPTF1'
    , 'ASTF1'
    , 'BKBF1'
    , 'COCF1'
    , 'DLAF1'
    , 'DMSF1'
    , 'GCVF1'
    , 'GENF1'
    , 'LKJF1'
    , 'MELF1'
    , 'MSBF1'
    , 'MYPF1'
    , 'PALF1'
    , 'RCYF1'
    , 'SJLF1'
    , 'SNFF1'
    , 'MRKF1'
    , 'NEPF1'
    , 'MACF1'
    , 'STEF1'
    , 'STIF1'
    , 'BFDF1'
    , 'DOUF1'
    , 'ELLF1'
    , 'FWBF1'
    , 'LIKF1'
    , 'LURF1'
    , 'MSPF1'
    , 'MTSF1'
    , 'RCKF1'
    , 'SBNF1'
    , 'SRNF1'
    , 'SUWF1'
    , 'WCXF1'
    , 'WSPF1'
    , 'TCGF1'
    , 'TELF1'
    , 'TOLF1'
    , 'THHF1'
    , 'TRJF1'
    , 'TRYF1'
    , 'WKLF1'
    , 'WKRF1'
    , 'WEKF1'
    , 'PINF1'
    , 'WTHF1'
    , 'WTMF1'
    , 'CRMF1'
    , 'DNLF1'
    , 'HLDF1'
    , 'TRBF1'
    , 'WRTF1'
    , 'OKGF1'
    , 'MLGF1'
    , 'MLYF1'
]
