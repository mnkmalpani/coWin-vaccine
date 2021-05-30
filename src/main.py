import sys
import hashlib
from datetime import datetime
import argparse
from utils import *
import os

header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
}

beneficiaries_data = {}

mobile = os.environ.get('MOBILE')
secret = "U2FsdGVkX1/VsmHZHLbdwntV6fMy5vTmAZhQtNlj00zdmonoostJjETavz9NKf578AFc3y1bgqAvLExdg48bRA=="
TOKEN_VALIDITY = 840 #taking 1 min buffer



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', help='Pass token directly')
    args = parser.parse_args()

    if not args.token:
        # generate otp
        generate_respose = generate_otp(mobile, header, secret)
        print("generate_respose recevied: ", generate_respose)
        # enter Otp
        otp = input("enter the otp: ")
        hashed_otp = hashlib.sha256(str(otp).encode('UTF-8')).hexdigest()
        # validate otp
        token_json = authenticateOtp(hashed_otp, generate_respose)
        print("Token recevied: ", token_json)
        # collect Barer token to check validity of the session
        token = token_json.get("token")
    else:
        token = args.token

    authentication = f"Bearer {token}"
    token_generated_time = datetime.now()

    # fetch beneficiaries data and print them
    beneficiaries_response = beneficiaries(authentication, header)
    beneficiaries_data = showBeneficiariesDetails(beneficiaries_response)

    # selection of the beneficiaries
    selection = input("Select the person to get vacinated: ").split()
    beneficiary_reference_ids = []
    for index in selection:
        beneficiary_reference_ids.append(beneficiaries_data.get(index).get('beneficiary_reference_id'))
    # select state & district
    states_response = getStates(authentication, header)
    showStates(states_response)
    state = input("Select the state: ")
    districts_response = getDistricts(state, header)
    showDistricts(districts_response)
    district = int(input("Select the district: "))

    # select date
    date = getDateFromUser()

    # get list of conditions
    fee_type, fee_type_flag, vaccine, vaccine_flag = getUserConditions()

    while (True):
        # find session
        sessions_dict = getSessionsByDistrict(district, date, header)
        sessions_list = sessions_dict.get("sessions", [])

        mini_slot = len(selection)
        min_age_limit = 18  # TODO should come from my selection

        for item in sessions_list:
            #create condition list
            condition = [item.get('min_age_limit') == min_age_limit,
                         item.get('available_capacity') >= mini_slot]
            if fee_type_flag:
                condition.append(fee_type == item.get('fee_type'))
            if vaccine_flag:
                condition.append(vaccine.upper() == item.get('vaccine'))

            if all(condition):
                for slot in item.get("slots"):
                    print("Slot available: ", item)
                    header["Authorization"] = authentication
                    response = book_slot(header=header, mini_slot=mini_slot, session_id=item.get('session_id'), slot=slot, beneficiary_reference_ids=beneficiary_reference_ids)
                    print("Booking response: ", response)
                    if response.status_code != 200:
                        print("Somthing went wrong, rechecking token validity")
                        #check validity
                        if (datetime.now() - token_generated_time).seconds <= TOKEN_VALIDITY:
                            print("Token is valid")
                        else:
                            # generate otp
                            token = str(input("Please paste the new token: "))
                            authentication = f"Bearer {token}"
                            token_generated_time = datetime.now()
                    else:
                        print(response.json())
                        sys.exit(0)

        print("No slots found, checking again")
        # check validity
        if (datetime.now() - token_generated_time).seconds > TOKEN_VALIDITY:
            print("Token is Invalid")
            token = str(input("Please paste the new token: "))
            authentication = f"Bearer {token}"
            token_generated_time = datetime.now()
