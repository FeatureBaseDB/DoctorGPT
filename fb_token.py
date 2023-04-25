import requests
import config
import sys
import json

# gather user/pass from the user
featurebase_username = input("Enter the FeatureBase Cloud username: ")
featurebase_password = input("Enter the FeatureBase Cloud password: ")

# login with credentials
url = 'https://id.featurebase.com'
data = {
    'USERNAME': featurebase_username,
    'PASSWORD': featurebase_password
}
headers = {
    'Content-Type': 'application/json'
}
response = requests.post(
    url=url,
    json=data,
    headers=headers
)

try:
    bearer_token = response.json().get('AuthenticationResult').get('IdToken')
except:
    print("Something went wrong. Check your login credentials and try again!")
    sys.exit()
    
# headers
headers = {
    'Authorization': 'Bearer %s' % bearer_token,
    'Content-Type': 'application/json'
}

# Make the request to the API and get the UUID
response = requests.get('https://api.featurebase.com/v2/users/current', headers=headers)
user_uuid = response.json().get('id')

# get token
url = "https://api.featurebase.com/v2/users/%s/keys" % user_uuid
data = {
    "description": "new key from python"
}
response = requests.post(
    url=url,
    json=data,
    headers=headers
)

try:
    print("Place the following token in config.py under `featurebase_token`: %s " % response.json().get('secret'))
except:
    print("Something went wrong. Check your login credentials and try again!")
