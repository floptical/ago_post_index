import requests
import json
from time import sleep


def generateToken():
    """
    Generate Token generates an access token in exchange for \
    user credentials that can be used by clients when working with the ArcGIS Portal API:
    http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000000m5000000
    """
    url = 'https://arcgis.com/sharing/rest/generateToken'
    data = {'username': 'your_user',
            'password': 'password',
            'referer': 'https://www.arcgis.com',
            'f': 'json'}
    return requests.post(url, data, verify=False).json()['token']

print("Generating token..")
token = generateToken()

index_json = {
  "indexes": [
  {
    "name": "some_idx",
    "fields": "some_field",
    "isUnique": 'false',
    "isAscending": 'false',
    "description": ""
  }
 ]
}
jsonData = json.dumps(index_json)

url = 'https://services.arcgis.com/98s3nsits7/ArcGIS/rest/admin/services/YOUR_DATASET/FeatureServer/0/addToDefinition'

print("Posting the index...")
headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
r = requests.post(f'{url}?token={token}', data = {'f': 'json', 'addToDefinition': jsonData }, headers=headers)

print(r)
print(r.status_code)
print(r.text)

# Delete from definition?
#sleep(5)
#url = 'https://services.arcgis.com/fLeGjb7u4uXqeF9q/ArcGIS/rest/admin/services/RTT_SUMMARY/FeatureServer/0/deleteFromDefinition'
