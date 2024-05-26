import json
import requests
from bs4 import BeautifulSoup

# Step 1: Retrieve initial cookie
username = "test@homeAssistant.com"
password = "randomPassword"
login_url = "https://login.ovoenergy.com.au/login"
session = requests.Session()
response = session.get(login_url)

# # Check if the cookies received
# if 'set-cookie' in response.headers:
#     cookie = response.headers['set-cookie']
# else:
#     print("Failed to retrieve cookie")
#     exit()

cookie = "cookieTest"

# Step 2: Submit the login form data
login_api_url = "https://login.ovoenergy.com.au/usernamepassword/login"
headers = {
    'accept-language': 'en-GB,en;q=0.9',
    'auth0-client': 'UnsureIfStaticOrUniquePerCustomer',
    'content-type': 'application/json',
    'cookie': cookie
}
data = {
    "client_id": "UnsureIfStaticOrUniquePerCustomer",
    "tenant": "ovoenergyau",
    "scope": "openid profile email offline_access",
    "audience": "https://login.ovoenergy.com.au/api",
    "_csrf": "Zc4Vf8Qr-YuivASXoUrMmnfEh8QXtyzHVzbo",
    "username": username,
    "password": password,
    "connection": "prod-myovo-auth"
}

response = session.post(login_api_url, json=data, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
token = soup.find('input', {'name': 'wresult'}).get('value', '')
print("Token:", token)

# Step 3: Make GraphQL API call
cookie = "cookieForTesting"
graphql_url = "https://my.ovoenergy.com.au/graphql"
graphql_headers = {
    'authorization': token,
    'content-type': 'application/json',
    'myovo-id-token': token,
    'cookie': cookie,
}
graphql_query = """
 {
   "operationName": "GetHourlyUsageData",
   "variables": {"input": {"id": "301234567", "system": "KALUZA"}},
   "query": "query GetHourlyUsageData($input: GetAccountInfoInput) "
 }
 """

response = session.post(graphql_url, headers=headers,
                        json=json.dumps(graphql_query))

# Check the HTTP status code
if response.status_code == 200:
    try:
        json_data = response.json()
        print(json_data)
    except ValueError as e:
        print("Failed to decode JSON:", e)
else:
    print(f"Request failed with status: {response.status_code}")
    print("Response content:", response.text)


# Step 4: Finish the script
print("Finish test script")
