import os, sys
import requests
import json
from time import sleep
from get_aws_secret import get_secret
import configparser


# Read from our global config file that should be one directory above.
if os.path.isfile('../aws-api-keys.ini'):
    config = configparser.ConfigParser()
    config.read('../aws-api-keys.ini')

    aws_access_key_id = config['AWS']['aws_access_key_id']
    aws_secret_access_key = config['AWS']['aws_secret_access_key']
    os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key_id
    os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret_access_key


maps_secrets = get_secret('AGO/maps.phl.data')
print(maps_secrets)
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


rtt_summary_idxs = {
        'address_high_ind': {'fields': ['address_high'], 'unique': 'false'},
        'address_low_frac': {'fields': ['address_low_frac'], 'unique': 'false'},
        'address_low_inde': {'fields': ['address_low'], 'unique': 'false'},
        'address_low_suff': {'fields': ['address_low_suffix'], 'unique': 'false'},
        'comp10_idx': {'fields': ['address_low','address_high','street_name','street_suffix'], 'unique': 'false'},
        'comp11_idx': {'fields': ['address_low','street_name','street_suffix'], 'unique': 'false'},
        'comp2_idx': {'fields': ['address_low','address_low_suffix','address_low_frac','street_predir','street_name','street_suffix'], 'unique': 'false'},
        'comp3_idx': {'fields': ['address_low','address_low_suffix','address_low_frac','street_name','street_suffix'], 'unique': 'false'},
        'comp4_idx': {'fields': ['address_low','address_low_frac','address_high','street_predir','street_name','street_suffix'], 'unique': 'false'},
        'comp5_idx': {'fields': ['address_low','address_low_frac','street_predir','street_name','street_suffix'], 'unique': 'false'},
        'comp6_idx': {'fields': ['address_low','address_low_suffix','address_high','street_predir','street_name','street_suffix'], 'unique': 'false'},
        'comp7_idx': {'fields': ['address_low','address_low_suffix','street_predir','street_name','street_suffix'], 'unique': 'false'},
        'comp8_idx': {'fields': ['address_low','address_low_suffix','street_name','street_suffix'], 'unique': 'false'},
        'comp9_idx': {'fields': ['address_low','address_high','street_name','street_suffix','street_predir'], 'unique': 'false'},
        'comp_idx': {'fields': ['address_low','address_low_suffix','address_low_frac','address_high','street_predir','street_name','street_suffix'], 'unique': 'false'},
        'docid_idx': {'fields': ['document_id'], 'unique': 'false'},
        'doctype_idx': {'fields': ['document_type'], 'unique': 'false'},
        'document_date_in': {'fields': ['document_date'], 'unique': 'false'},
        'grantees_idx': {'fields': ['grantees'], 'unique': 'false'},
        'grantors_idx': {'fields': ['grantors'], 'unique': 'false'},
        'matchregmap_idx': {'fields': ['matched_regmap'], 'unique': 'false'},
        'obj_idx': {'fields': ['objectid'], 'unique': 'false'},
        'opa_idx': {'fields': ['opa_account_num'], 'unique': 'false'},
        'record_id_unique': {'fields': ['record_id'], 'unique': 'true'},
        'reg_map_id_idx': {'fields': ['reg_map_id'], 'unique': 'false'},
        'state_tax_amount': {'fields': ['state_tax_amount'], 'unique': 'false'},
        'streetname_idx': {'fields': ['street_name'], 'unique': 'false'},
        'streetpostdir_id': {'fields': ['street_postdir'], 'unique': 'false'},
        'street_predir_in': {'fields': ['street_predir'], 'unique': 'false'},
        'street_suffix_in': {'fields': ['street_suffix'], 'unique': 'false'},
        'total_considerat': {'fields': ['total_consideration'], 'unique': 'false'},
        'zipcode_idx': {'fields': ['zip_code'], 'unique': 'false'}
        }


for key,value in rtt_summary_idxs.items():
    print('\n')

    fields = ','.join(rtt_summary_idxs[key]['fields'])

    index_json = {
      "indexes": [
      {
        "name": key,
        "fields": fields,
        "isUnique": rtt_summary_idxs[key]['unique'],
        "isAscending": 'true',
        "description": ""
      }
     ]
    }
    jsonData = json.dumps(index_json)
    print(jsonData)

    # This endpoint is publicly viewable on AGO while not logged in.
    url = 'https://services.arcgis.com/fLeGjb7u4uXqeF9q/arcgis/rest/admin/services/RTT_SUMMARY/FeatureServer/0/addToDefinition'

    print("Posting the index...")
    headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    r = requests.post(f'{url}?token={token}', data = {'f': 'json', 'addToDefinition': jsonData }, headers=headers, timeout=360)

    print(r)
    #print(r.status_code)
    print(r.text)
    sleep(2)

# Delete from definition?
#sleep(5)
#url = 'https://services.arcgis.com/fLeGjb7u4uXqeF9q/ArcGIS/rest/admin/services/RTT_SUMMARY/FeatureServer/0/deleteFromDefinition'
