import json
from readable_password import readable_password as rpwd
from fstl_api_handler import fstl_api
import os
import argparse
import yaml


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_import_path", type=str, help="path to json to import")
    args = parser.parse_args()
    return args


def normalize_json_data(json_data):
    if type(json_data) == list:
        return json_data
    elif type(json_data) == dict:
        return [json_data]


def load_json(path_to_json: str):
    with open(path_to_json, "r") as json_filehandler:
        json_loaded = json.load(json_filehandler)
    return normalize_json_data(json_loaded)


def get_useraccount_type(user_data):    
    if "children" in user_data:
        if user_data["children"] is not None:
            return "Eltern"
        else:
            return "Team_FSTL"
    elif "input_role" in user_data:
        if user_data["input_role"] is not None:
            return user_data["input_role"]
        else:
            return "Team_FSTL"


def check_if_user_exists(user_data, fstl):
    if get_useraccount_type(user_data) == "Eltern":
        display_name = f'{user_data["parents"]["1"]["inputParentForename"]} {user_data["parents"]["1"]["inputParentSurname"]}'
    else:
        if 'Forename' in user_data and 'Surname' in user_data:
            display_name = f"{user_data['Forename']} {user_data['Surname']}"
        elif 'inputForename' in user_data and 'inputSurname' in user_data:
            display_name = f"{user_data['inputForename']} {user_data['inputSurname']}"
    return fstl.check_if_user_exists(display_name)


def get_group_for_user(user_data, path_to_mapfiles="data/privileged_members/"):
    priv_files = os.listdir(path_to_mapfiles)
    # check if user data is in list of privileged users
    # return the corresponding role
    account_type = get_useraccount_type(user_data)
    if account_type == "Team_FSTL":
        return "Team_FSTL"
    elif account_type == "Eltern":
        for group in priv_files:
            with open(f"{path_to_mapfiles}{group}", "r") as filehandler:
                for line in filehandler:
                    for element in user_data["parents"].items():
                        forename = element[1]["inputParentForename"]
                        if "inputParentSurname" in element[1]:
                            surname = element[1]["inputParentSurname"]
                        elif "inputParentSurename" in element[1]:
                            surname = element[1]["inputParentSurename"]
                        if f"{forename} {surname}" in line:
                            return group
        return "Eltern"
    elif "inputRole" in user_data:
        return user_data["inputRole"]
    else:
        return None


def json_dict_2_multiline_string(json_dict):
    multiline_string = ""
    for element in json_dict.items():
        for item in element[1]:
            # append to csv string, apply correct names
            multiline_string += f"{element[1][item].replace('primary', 'Grundschule').replace('secondary', 'Gesamtschule')} "
        # append newline to end csv row correctly
        multiline_string += "\n"
    return multiline_string[0:-1]


def create_params_for_user(user_data):
    group = get_group_for_user(user_data, path_to_mapfiles="data/privileged_members/")
    email = user_data["inputEmail"]
    username = email

    if get_useraccount_type(user_data) == "Eltern":
        name = f'{user_data["parents"]["1"]["inputParentForename"]} {user_data["parents"]["1"]["inputParentSurname"]}'
    else:
        name = f'{user_data["inputForename"]} {user_data["inputSurname"]}'

    # create readable random password
    password = rpwd.readable_password(
        length=8, incl_upper=True, incl_digit=True, incl_punc=False
    )
    group = get_group_for_user(user_data)
    params = {
        "name": name,
        "username": username,
        "email": email,
        "group": group,
        "password": password,
    }
    if "parents" in user_data:
        params["sorgeberechtigte"] = json_dict_2_multiline_string(user_data["parents"])
    if "children" in user_data:
        params["kinder"] = json_dict_2_multiline_string(user_data["children"])
    return params


def get_api_credentials():
    return os.getenv("FSTL_CYCLOS_ADMIN_USERNAME"),os.getenv("FSTL_CYCLOS_ADMIN_PASSWORD")


def get_export_path(import_path):
    if "cyclos_data" in import_path:
        json_export_path = import_path.replace("_cyclos_data", "_generated_users")
    elif "cyclos_users_data" in import_path:
        json_export_path = import_path.replace("_cyclos_users_data", "_generated_users")
    elif "cyclos_staff_data" in import_path:
        json_export_path = import_path.replace("_cyclos_staff_data", "_generated_staff")
    export_path = json_export_path.replace('import','export')
    return export_path


def check_and_create_export_file(json_export_path):
    if not os.path.exists("/".join(json_export_path.split("/")[:-1])):
        os.makedirs("/".join(json_export_path.split("/")[:-1]))
    if not os.path.isfile(json_export_path):
        print('sdfasdf')
        with open(json_export_path, mode="w", encoding="utf-8") as f:
            json.dump([], f)
    return

def main():

    args = parse()

    json_import_path = args.json_import_path
    json_export_path = get_export_path(json_import_path)
    print(json_export_path)

    FSTL_CYCLOS_ADMIN_USERNAME, FSTL_CYCLOS_ADMIN_PASSWORD = get_api_credentials()
    print("Initializing API to interact with Cyclos FSTL Community.")
    fstl = fstl_api(FSTL_CYCLOS_ADMIN_USERNAME, FSTL_CYCLOS_ADMIN_PASSWORD)

    loaded_data = load_json(json_import_path)
    print(f"{len(loaded_data)} users in import file")
    
    import_data = []
    for user in loaded_data:
        print(user)
        if not check_if_user_exists(user, fstl):
            import_data.append(user)

    print(f"Importing {len(import_data)} non-existent users")

    if len(import_data)>0:
        check_and_create_export_file(json_export_path)

    print(import_data)

    for user_data in import_data:        
        user_params = create_params_for_user(user_data)
        export_values = ["username", "password"]
        print(user_params)
        export_dict = {key: user_params[key] for key in export_values}
        print(export_dict)
        with open(json_export_path) as fp:
            listObj = json.load(fp)
        if not any(d["username"] == export_dict["username"] for d in listObj):
            listObj.append(export_dict)
        else:
            for elem in listObj:
                if elem["username"] == export_dict["username"]:
                    elem["password"] = export_dict["password"]
        if fstl.create_user(user_params):    
            print('hallo') 
            with open(json_export_path, mode="w", encoding="utf-8") as json_file:
                print('hallo2')
                json.dump(listObj, json_file, indent=4, separators=(",", ": "))



if __name__ == "__main__":
    main()
