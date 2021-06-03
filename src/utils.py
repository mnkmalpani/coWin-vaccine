from prettytable import PrettyTable
from captcha import captcha_builder
from datetime import date, datetime, timedelta
import requests
import sys
import hashlib
from decouple import config
import time

resources = {
    'generateMobileOTP': "/api/v2/auth/generateMobileOTP",
    'validateMobileOtp': '/api/v2/auth/validateMobileOtp',
    'beneficiaries': '/api/v2/appointment/beneficiaries',
    'states': '/api/v2/admin/location/states',
    'districts': '/api/v2/admin/location/districts/',
    'schedule': '/api/v2/appointment/schedule',
    'getRecaptcha': '/api/v2/auth/getRecaptcha'
}

coWinUrl = "https://cdn-api.co-vin.in"

header_otp = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
}

header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    , 'content-type': 'application/json'
    , 'origin': 'https://selfregistration.cowin.gov.in'
    , 'sec-fetch-site': 'cross-site'
    , 'sec-fetch-mode': 'cors'
    , 'sec-fetch-dest': 'empty'
    , 'referer': 'https://selfregistration.cowin.gov.in/'
}

beneficiaries_data = {}
states = {}

mobile = 9880267075
secret = "U2FsdGVkX1/VsmHZHLbdwntV6fMy5vTmAZhQtNlj00zdmonoostJjETavz9NKf578AFc3y1bgqAvLExdg48bRA=="
TOKEN_VALIDITY = 840  # taking 1 min buffer


def check_token_status(authentication, header):
    header["Authorization"] = authentication
    url = coWinUrl + resources.get('beneficiaries')
    response = requests.get(url, headers=header)
    if response.status_code == 200:
        return True
    else:
        return False


def generate_otp(mobile, header, secret):
    data = {
        'mobile': mobile,
        'secret': secret
    }
    url = coWinUrl + resources.get("generateMobileOTP")
    response = requests.post(url=url, json=data, headers=header)
    if response.status_code != 200:
        print("Somthing went wrong, regenerating otp")
    else:
        return response.json()


def authenticateOtp(hashed_otp, generate_respose):
    data = {
        'otp': hashed_otp,
        'txnId': generate_respose['txnId']
    }
    url = coWinUrl + resources.get("validateMobileOtp")
    response = requests.post(url=url, json=data, headers=header)
    if response.status_code == 401:
        print("Unauthenticated Access, please check your otp")
    elif response.status_code == 200:
        return response.json()
    else:
        print("Bad Request or Internal Server Error while authentication otp")
        sys.exit(1)


def beneficiaries(authentication, header):
    header["Authorization"] = authentication
    url = coWinUrl + resources.get('beneficiaries')
    response = requests.get(url, headers=header)
    if response.status_code != 200:
        print("Token is not valid, please provide a valid token")
        sys.exit(1)
    else:
        return response.json()


def showBeneficiariesDetails(beneficiaries_response):
    if not beneficiaries_response:
        print("No beneficiaries added")
        return
    table = PrettyTable(['Name', 'Age', 'vaccination_status', 'vaccine'])
    sno = 1
    for item in beneficiaries_response.get('beneficiaries'):
        table.add_row(
            [item.get('name'), (int(datetime.now().year) - int(item.get('birth_year'))), item.get('vaccination_status'),
             item.get('vaccine')])
        beneficiaries_data[str(sno)] = {
            'beneficiary_reference_id': item.get('beneficiary_reference_id'),
            'name': item.get('name'),
            'age': (int(datetime.now().year) - int(item.get('birth_year'))),
            'vaccination_status': item.get('vaccination_status'),
            'vaccine': item.get('vaccine')
        }
        sno = sno + 1
    print(table)
    return beneficiaries_data


def getStates(authentication, header):
    header["Authorization"] = authentication
    url = coWinUrl + resources.get('states')
    response = requests.get(url, headers=header)
    if response.status_code != 200:
        print("Somthing went wrong, regenerating otp")
    else:
        return response.json()


def showStates(states_response):
    table = PrettyTable(['id', 'name'])
    for item in states_response.get('states'):
        table.add_row([item.get('state_id'), item.get('state_name')])
        states[item.get('state_id')] = item.get('state_name')
    print("<========================  STATE NAMES  ============================>")
    print(table)


def getDistricts(state, header):
    url = coWinUrl + resources.get('districts') + state
    response = requests.get(url=url, headers=header)
    if response.status_code != 200:
        print("Somthing went wrong, regenerating otp")
    else:
        return response.json()


def showDistricts(districts_response):
    table = PrettyTable(['id', 'name'])
    for item in districts_response.get('districts'):
        table.add_row([item.get('district_id'), item.get('district_name')])
        states[item.get('state_id')] = item.get('state_name')

    print("<========================  DISTRICT NAMES  ============================>")
    print(table)


def getDateFromUser():
    when_to_book = int(input("1 -> today, 2 -> Tomorrow, Default 2") or "2")
    if when_to_book == 2:
        return (date.today() + timedelta(days=1)).strftime('%d-%m-%Y')
    elif when_to_book == 1:
        return date.today().strftime('%d-%m-%Y')
    else:
        print("Input right value")
        sys.exit(1)


def getSessionsByDistrict(districts, date, header):
    all_sessions = []
    for district in districts:
        session_path = f"/api/v2/appointment/sessions/public/findByDistrict?district_id={district}&date={date}"
        url = coWinUrl + session_path
        response = requests.get(url=url, headers=header)
        if response.status_code != 200:
            print(
                "Somthing went wrong while fetching the sessions, coWin must be under heavy traffic. Please try later!")
            sys.exit(1)
        else:
            curr_dist_session_list = response.json()
            all_sessions.extend(curr_dist_session_list.get('sessions', []))
    return {'sessions': all_sessions}


def getUserConditions():
    fee_type_flag = True
    vaccine_flag = True
    fee_type_preference = int(input("Select the fee type: 1) Free  2) paid, enter) No preference :") or "0")
    if fee_type_preference == 1:
        fee_type = 'Free'
    elif fee_type_preference == 2:
        fee_type = 'Paid'
    else:
        fee_type = ''
        fee_type_flag = False

    vaccine_type_preference = int(
        input("Select the Vaccine type: 1) Covaxine  2) Covishield, enter) No preference :") or "0")
    if vaccine_type_preference == 1:
        vaccine_type = 'COVAXIN'
    elif vaccine_type_preference == 2:
        vaccine_type = 'COVISHIELD'
    else:
        vaccine_type = ''
        vaccine_flag = False

    return fee_type, fee_type_flag, vaccine_type, vaccine_flag


def generate_captcha(request_header):
    print('================================= GETTING CAPTCHA ==================================================')
    CAPTCHA_URL = coWinUrl + resources.get('getRecaptcha')
    resp = requests.post(CAPTCHA_URL, headers=request_header)
    print(f'Captcha Response Code: {resp.status_code}')

    if resp.status_code == 200:
        return captcha_builder(resp.json())


def book_slot(header, mini_slot, session_id, slot, beneficiary_reference_ids):
    url = coWinUrl + resources.get('schedule')
    data = {
        'dose': mini_slot,
        'session_id': session_id,
        'slot': slot,
        'beneficiaries': beneficiary_reference_ids
    }
    captcha = generate_captcha(request_header=header)
    data['captcha'] = captcha
    return requests.post(url=url, json=data, headers=header)

def generate_and_validate_otp(mobile, header_otp, secret, auto):
    # generate otp
    global otp_message
    generate_respose = generate_otp(mobile, header_otp, secret)
    print("generate_respose recevied: ", generate_respose)
    # enter Otp
    if not auto:
        otp = input("enter the otp: ")
    else:
        print("Fetching otp after 10secs")
        time.sleep(10)
        i = 1
        while i <= 6:
            kvdb_url = config('KVDB_URL') + '/' + str(mobile)
            otp_message_response = requests.get(kvdb_url)
            otp_message = otp_message_response.text
            print("otp_message output:", otp_message)
            if len(otp_message) == 0:
                i = i + 1
                time.sleep(5)
            else:
                i = 999
        if i == 7:
            print("No otp received from kvdb.io, please try again")
            sys.exit(1)
        otp = otp_message[37:43]
    hashed_otp = hashlib.sha256(str(otp).encode('UTF-8')).hexdigest()
    token_json = authenticateOtp(hashed_otp, generate_respose)
    print("Token recevied: ", token_json)
    # collect Barer token to check validity of the session
    return token_json.get("token")