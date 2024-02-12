import json
from fstl_api_handler import fstl_api
import os
import argparse
from datetime import datetime
import pytz



def get_api_credentials():
    return os.getenv("FSTL_CYCLOS_ADMIN_USERNAME"),os.getenv("FSTL_CYCLOS_ADMIN_PASSWORD")

def get_statefile_path():
    return os.getenv("LAST_STATE_FILE_PATH_PATH")

def get_active_advertisements(): 
    FSTL_CYCLOS_ADMIN_USERNAME, FSTL_CYCLOS_ADMIN_PASSWORD = get_api_credentials()
    fstl = fstl_api(FSTL_CYCLOS_ADMIN_USERNAME, FSTL_CYCLOS_ADMIN_PASSWORD)

    all_advertisements = fstl.get_all_advertisements()
    active_advertisements = []

    now = datetime.now(pytz.utc)  # Aktuelle Zeit in UTC

    for ad in all_advertisements:
        if ad['status'] != 'expired':
            begin = datetime.fromisoformat(ad['publicationPeriod']['begin'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(ad['publicationPeriod']['end'].replace('Z', '+00:00'))
            if begin <= now <= end:
                active_advertisements.append(ad)

    return active_advertisements

def read_last_saved_ads(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def write_new_ads(filename, ads):
    with open(filename, 'w') as file:
        json.dump(ads, file)

def find_new_ads(current_ads, last_saved_ads):
    last_saved_ids = {ad['id'] for ad in last_saved_ads}
    return [ad for ad in current_ads if ad['id'] not in last_saved_ids]

def main():

    filename = get_statefile_path()
    last_saved_ads = read_last_saved_ads(filename)
    current_ads = get_active_advertisements()
    new_ads = find_new_ads(current_ads, last_saved_ads)

    if new_ads:
        print("Es gibt neue aktive Anzeigen seit dem letzten Aufruf:")
        for ad in new_ads:
            print(ad)
        # Aktualisieren Sie die Datei mit den aktuellen Anzeigen
        write_new_ads(filename, current_ads)
    else:
        print("Keine neuen aktiven Anzeigen zum aktuellen Zeitpunkt.")


if __name__ == "__main__":
    main()
