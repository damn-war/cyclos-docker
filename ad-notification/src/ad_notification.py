import json
from fstl_api_handler import fstl_api
import os
import argparse
from datetime import datetime
import pytz



def get_api_credentials():
    return os.getenv("FSTL_CYCLOS_ADMIN_USERNAME"),os.getenv("FSTL_CYCLOS_ADMIN_PASSWORD")

def get_statefile_path():
    return os.getenv("LAST_STATE_FILE_PATH")

def get_export_path():
    return os.getenv("EXPORT_PATH")    

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
            data = json.load(file)
            return data.get('ads', []), data.get('last_check')
    except FileNotFoundError:
        return [], None

def write_new_ads(filename, ads, last_check):
    data = {
        'ads': ads,
        'last_check': last_check
    }
    with open(filename, 'w') as file:
        json.dump(data, file)

def find_new_ads(current_ads, last_saved_ads):
    last_saved_ids = {ad['id'] for ad in last_saved_ads}
    return [ad for ad in current_ads if ad['id'] not in last_saved_ids]

def export_new_ads(export_folder, ads, timestamp):
    if not os.path.exists(export_folder):
        os.makedirs(export_folder)
    export_filename = os.path.join(export_folder, f"new_ads_{timestamp}.json")
    with open(export_filename, 'w') as file:
        json.dump(ads, file)

def main():

    filename = get_statefile_path()
    export_folder = get_export_path()
    last_saved_ads, last_check = read_last_saved_ads(filename)
    current_ads = get_active_advertisements()
    new_ads = find_new_ads(current_ads, last_saved_ads)

    now_iso = datetime.now(pytz.utc).isoformat()

    if new_ads:
        print("Es gibt neue aktive Anzeigen seit dem letzten Aufruf:")
        for ad in new_ads:
            print(ad)
        write_new_ads(filename, current_ads, now_iso)
        export_new_ads(export_folder, new_ads, now_iso.replace(':', '-'))  # Ersetzt ':' in der Zeitstempel für Dateikompatibilität

    else:
        print("Keine neuen aktiven Anzeigen zum aktuellen Zeitpunkt.")


if __name__ == "__main__":
    main()
