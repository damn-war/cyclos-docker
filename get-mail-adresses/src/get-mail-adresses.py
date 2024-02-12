import json
from fstl_api_handler import fstl_api
import os
import argparse
from datetime import datetime



def get_api_credentials():
    return os.getenv("FSTL_CYCLOS_ADMIN_USERNAME"),os.getenv("FSTL_CYCLOS_ADMIN_PASSWORD")


def get_export_path():
    return os.getenv("EXPORT_PATH")    

def get_mail_adresses():
    FSTL_CYCLOS_ADMIN_USERNAME, FSTL_CYCLOS_ADMIN_PASSWORD = get_api_credentials()
    fstl = fstl_api(FSTL_CYCLOS_ADMIN_USERNAME, FSTL_CYCLOS_ADMIN_PASSWORD)
    users = fstl.get_users()
    mails = []
    for user in users:
        user_info = fstl.get_user_information(user["id"])
        if 'email' in user_info:
            mails.append(user_info['email'])
    return mails



def main():
    export_folder = get_export_path()
    email_addresses = get_mail_adresses()
    with open(os.path.join(export_folder, 'email_addresses.json'), 'w') as file:
        json.dump(email_addresses, file)



if __name__ == "__main__":
    main()
