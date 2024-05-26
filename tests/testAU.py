import requests

# Step 1: Retrieve initial cookie
login_url = "https://login.ovoenergy.com.au/login"
session = requests.Session()
response = session.get(login_url)

# # Check if the cookies received
# if 'set-cookie' in response.headers:
#     cookie = response.headers['set-cookie']
# else:
#     print("Failed to retrieve cookie")
#     exit()

# 'cookie': cookie - use this if needed for step 2

# Step 2: Submit the login form data
login_api_url = "https://login.ovoenergy.com.au/usernamepassword/login"
headers = {
    'accept-language': 'en-GB,en;q=0.9',
    'auth0-client': 'FakeAuth',
    'content-type': 'application/json'
}
data = {
    "client_id": "FakeClientID",
    # make sure to replace further sensitive data if needed
    # the rest of the payload as per your data
    "username": "Fakeemail@test.com",
    "password": "FakePassword",
    "connection": "prod-myovo-auth"
}

response = session.post(login_api_url, json=data, headers=headers)
print(response)
token = response.json().get('wresult.value', '')
if not token:
    print("Failed to get the authentication token.")
    exit()

# Step 3: Make GraphQL API call
graphql_url = "https://my.ovoenergy.com.au/graphql"
graphql_headers = {
    'authorization': token,
    'content-type': 'application/json',
    'myovo-id-token': token,
    # the rest of the headers as per your data
}
graphql_query = """
{
  "operationName": "GetHourlyUsageData",
  "variables": {"input": {"id": "testID", "system": "KALUZA"}},
  "query": "query GetHourlyUsageData($input: GetAccountInfoInput) {...}"
}
"""
response = session.post(
    graphql_url, headers=graphql_headers, json=graphql_query)
print(response.json())

# Step 4: Finish the script
print("Finish test script")
