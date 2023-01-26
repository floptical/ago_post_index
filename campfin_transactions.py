import os, sys
import requests
import json
from time import sleep
from get_aws_secret import get_secret
import configparser

# Change to our script dir for the relative file path below
script_directory = os.path.dirname(os.path.realpath(__file__))
pid = os.getpid()
os.chdir(script_directory)

# Read from our global config file that should be one directory above.
if os.path.isfile('../aws-api-keys.ini'):
    config = configparser.ConfigParser()
    config.read('../aws-api-keys.ini')

    aws_access_key_id = config['AWS']['aws_access_key_id']
    aws_secret_access_key = config['AWS']['aws_secret_access_key']
    os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key_id
    os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret_access_key


maps_secrets = get_secret('AGO/maps.phl.data')
ago_user = 'maps.phl.data'
ago_pw = maps_secrets['password']


def generateToken():
    """
    Generate Token generates an access token in exchange for \
    user credentials that can be used by clients when working with the ArcGIS Portal API:
    http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000000m5000000
    """
    url = 'https://arcgis.com/sharing/rest/generateToken'
    data = {'username': ago_user,
            'password': ago_pw,
            'referer': 'https://www.arcgis.com',
            'f': 'json'}
    return requests.post(url, data, verify=False).json()['token']

print("Generating token..")
token = generateToken()

campfin_transactions_idx = ['transaction_date',
                            'transaction_type',
                            'transaction_amount',
                            'filer_name',
                            'filer_type',
                            'filer_local_flag',
                            'filer_local_flag_desc',
                            'entity_name',
                            'entity_type',
                            'entity_local_flag',
                            'entity_local_flag_desc',
                            'report_year',
                            'report_election_date',
                            'election_type',
                            'filer_id',
                            'filer_city',
                            'filer_state',
                            'filer_zip',
                            'filer_actv_cand_flag',
                            'filer_actv_city_cand_flag',
                            'filer_actv_city_cand_desg_flag',
                            'filer_candidate_name',
                            'candidate_office',
                            'office_level',
                            'candidate_party',
                            'candidate_district_num',
                            'candidate_district_name',
                            'entity_city',
                            'entity_state',
                            'entity_zip',
                            'report_cycle_code']


for field in campfin_transactions_idx:
    print('\n')

    index_json = {
      "indexes": [
      {
        "name": field + '_idx',
        "fields": field,
        "isUnique": 'false',
        "isAscending": 'true',
        "description": ""
      }
     ]
    }
    jsonData = json.dumps(index_json)

    # This endpoint is publicly viewable on AGO while not logged in.
    url = 'https://services.arcgis.com/fLeGjb7u4uXqeF9q/arcgis/rest/admin/services/CAMPFIN_TRANSACTIONS/FeatureServer/0/addToDefinition'

    print(f"Posting the index for '{field}'..")
    headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    r = requests.post(f'{url}?token={token}', data = {'f': 'json', 'addToDefinition': jsonData }, headers=headers, timeout=360)

    if 'Invalid definition' in r.text:
        print('''
        Index appears to already be set, got "Invalid Definition" error (this is usually a good thing, but still
        possible your index was actually rejected. ESRI just doesnt code in proper errors).
        ''')
    else:
        print(r.text)
    sleep(2)

# Delete from definition?
#sleep(5)
#url = 'https://services.arcgis.com/fLeGjb7u4uXqeF9q/ArcGIS/rest/admin/services/RTT_SUMMARY/FeatureServer/0/deleteFromDefinition'
