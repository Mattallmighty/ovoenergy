import json
import requests
from bs4 import BeautifulSoup

# Specify your username & password here
username = "RandomEmail@outlook.com"
password = "RandomPassword"

headers = {
    'Content-Type': 'application/json',
    'auth0-client': 'eyJuYW1lIjoiYXV0aDAuanMtdWxwIiwidmVyc2lvbiI6IjkuMjQuMSJ9',
    'cookie': '_csrf=ZO4zbJdLowH07jxRDIEH1Zdb'
}

data_login = {
    "client_id": "5JHnPn71qgV3LmF3I3xX0KvfRBdROVhR",
    "redirect_uri": "https://my.ovoenergy.com.au?login=oea",
    "tenant": "ovoenergyau",
    "response_type": "code",
    "scope": "openid profile email offline_access",
    "audience": "https://login.ovoenergy.com.au/api",
    "_csrf": "Xlb8re1m-Wqsc-ABqgAEMwlSz3V2aTuqOs0g",
    "username": username,
    "password": password,
    "connection": "prod-myovo-auth"
}
token_response = None

# Step 1: Login
loginResponse = requests.post(
    'https://login.ovoenergy.com.au/usernamepassword/login', headers=headers, data=json.dumps(data_login))
if loginResponse.status_code == 200:
    soup = BeautifulSoup(loginResponse.text, 'html.parser')
    hidden_form = soup.find('form', attrs={'name': 'hiddenform'})
    if hidden_form:
        login_data = {field.get('name'): field.get('value')
                      for field in hidden_form.find_all('input')}
        wresult = login_data.get('wresult')
        wctx = login_data.get('wctx')
        print('Successful login')
        print("wresult:", wresult)
        print("wctx:", wctx)
        # Step 2: Login Part 2??
        # Somehow need to define client_id and code. Lost how to do this?? Not coming from wresult or wctx..grrr
        code_verifier = "RandomCode"
        code = "RandomCode"
        # Step 3: If login successful, Get Token
        headers = {
            'accept': '*/*',
            'auth0-client': 'eyJuYW1lIjoiYXV0aDAtcmVhY3QiLCJ2ZXJzaW9uIjoiMi4yLjQifQ==',
            'content-type': 'application/x-www-form-urlencoded'
        }
        data_token = {
            "client_id": "5JHnPn71qgV3LmF3I3xX0KvfRBdROVhR",
            "grant_type": "authorization_code",
            "code_verifier": code_verifier,
            "code": code,
            "redirect_uri": "https://my.ovoenergy.com.au?login=oea"
        }
        token_response = requests.post(
            'https://login.ovoenergy.com.au/oauth/token', headers=headers, data=data_token)

        if token_response.status_code == 200:
            print("Token successful.", token_response.json())
            json_response = token_response.json()
            access_token = json_response['access_token']
            refresh_token = json_response['refresh_token']
            id_token = json_response['id_token']
            print("Access Token:", access_token)

            # Step 4: If token successful, Get Account Number
            headers = {
                'Authorization': access_token,
                'Myovo-Id-Token': id_token,
                'Content-Type': 'application/json',
                'cookie': '_csrf=ZO4zbJdLowH07jxRDIEH1Zdb'
            }

            data_getAccountInfo = {
                "operationName": "GetContactInfo",
                "variables": {"input": {"email": username}},
                "query": """
                query GetContactInfo($input: GetContactInfoInput!) {
                    GetContactInfo(input: $input) {
                        accounts {
                            id
                            number
                            customerId
                            customerOrientatedBalance
                            closed
                            system
                            hasSolar
                            supplyAddress {
                                buildingName
                                buildingName2
                                lotNumber
                                flatType
                                flatNumber
                                floorType
                                floorNumber
                                houseNumber
                                houseNumber2
                                houseSuffix
                                houseSuffix2
                                streetSuffix
                                streetName
                                streetType
                                suburb
                                state
                                postcode
                                countryCode
                                country
                                addressType
                                __typename
                            }
                            __typename
                        }
                    }
                }
                """
            }

            response = requests.post('https://my.ovoenergy.com.au/graphql',
                                     headers=headers, data=json.dumps(data_getAccountInfo))
            print(f"Status Code: {response.status_code}")
        print("Response Text:", response.text)

        if response.status_code == 200:
            json_response = response.json()
            accountID = json_response.get('data', {}).get(
                'GetContactInfo', {}).get('accounts', [{}])[0].get('id', '')
            system = json_response.get('data', {}).get(
                'GetContactInfo', {}).get('accounts', [{}])[0].get('system', '')
            if accountID:
                print("Account ID:", accountID)
                print("Account ID:", system)
                # Step 5: If Account Number successful, Get Hourly energy usage
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": access_token,
                    "myovo-id-token": id_token,
                    "cookie": "__zlcmid=1M3mlFcNGuNAJWk"
                }
                data_getHourlyUsage = {
                    "query": """
                    query GetHourlyUsageData($input: GetAccountInfoInput!) {
                        GetAccountInfo(input: $input) {
                            id
                            usage {
                                hourly {
                                    ...UsageDataParts
                                    __typename
                                }
                                __typename
                            }
                            __typename
                        }
                    }

                    fragment UsageDataParts on UsageData {
                        export {
                            charge {
                                value
                                type
                                __typename
                            }
                            consumption
                            periodFrom
                            periodTo
                            charge {
                                value
                                type
                                __typename
                            }
                            __typename
                        }
                        solar {
                            charge {
                                value
                                type
                                __typename
                            }
                            consumption
                            periodFrom
                            periodTo
                            charge {
                                value
                                type
                                __typename
                            }
                            __typename
                        }
                        __typename
                    }""",
                    "variables": {
                        "input": {
                            "id": accountID,
                            "system": system
                        }
                    }
                }

                hourlyenergyresponse = requests.post(
                    'https://my.ovoenergy.com.au/graphql', headers=headers, json=data_getHourlyUsage)
                if hourlyenergyresponse.status_code == 200 and 'application/json' in hourlyenergyresponse.headers.get('Content-Type', ''):
                    try:
                        print(f"JSON Response: {json.dumps(
                            hourlyenergyresponse.json(), indent=4)}")
                    except json.JSONDecodeError as e:
                        print("Failed to decode JSON:", e)
                else:
                    print("hourlyenergyresponse Error! ", "Status code is: ",
                          hourlyenergyresponse.status_code)
                    print(hourlyenergyresponse.text)
            else:
                print("Account ID not found.")
        else:
            print(f"Error from server: {response.text}")
    else:
        error_response = token_response.json()
        print(f"Error during getting token: {
              token_response.status_code} Error response: {error_response}")

else:
    print("No form found in HTML response.")
