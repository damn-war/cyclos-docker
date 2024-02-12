import json
from readable_password import readable_password as rpwd
from fstl_api_handler import fstl_api
import os
import argparse


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
        else:
            display_name = None
    return fstl.check_if_user_exists(display_name)


def get_group_for_user(user_data, path_to_mapfiles):
    priv_files = os.listdir(path_to_mapfiles)
    # check if user data is in list of privileged users
    # return the corresponding role
    account_type = get_useraccount_type(user_data)
    if account_type == "Team_FSTL":
        return "Team_FSTL"
    elif account_type == "Eltern":
        for group in priv_files:
            with open(f"{path_to_mapfiles}/{group}", "r") as filehandler:
                for line in filehandler:
                    for element in user_data["parents"].items():
                        forename = element[1]["inputParentForename"]
                        if "inputParentSurname" in element[1]:
                            surname = element[1]["inputParentSurname"]
                        elif "inputParentSurename" in element[1]:
                            surname = element[1]["inputParentSurename"]
                        else:
                            surname = None
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


def create_params_for_user(user_data, path_to_mapfiles):
    group = get_group_for_user(user_data, path_to_mapfiles=path_to_mapfiles)
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
    group = get_group_for_user(user_data, path_to_mapfiles)
    params = {
        "name": name,
        "username": username,
        "email": email,
        "group": group,
        "password": password,
        "state": "created"
    }
    if "parents" in user_data:
        params["sorgeberechtigte"] = json_dict_2_multiline_string(user_data["parents"])
    if "children" in user_data:
        params["kinder"] = json_dict_2_multiline_string(user_data["children"])
    return params


def get_api_credentials():
    return os.getenv("FSTL_CYCLOS_ADMIN_USERNAME"),os.getenv("FSTL_CYCLOS_ADMIN_PASSWORD")


def get_folder_paths():
    return os.getenv("IMPORT_FOLDER_PATH"),os.getenv("EXPORT_FOLDER_PATH"),os.getenv("PRIVILEGED_MAPPING_FOLDER")


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
        with open(json_export_path, mode="w", encoding="utf-8") as f:
            json.dump([], f)
    return


def check_if_folder_exist(folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        print(f"The folder {folder_path} exists!")
    else:
        raise Exception(f"The folder {folder_path} does not exist!")


def sync_users_for_single_file(json_import_path, fstl, privileged_mapping_folder):
    json_export_path = get_export_path(json_import_path)
    import_data = load_json(json_import_path)
    print(f"{len(import_data)} users in import file")
    # check if there exist an export file for the iomport file
    if os.path.exists(json_export_path) and os.path.isfile(json_export_path):
        print(f"The file {json_export_path} exists!")
        with open(json_export_path) as export_file_handler:
            export_list = json.load(export_file_handler)
            for import_user in import_data:
                print(f"Checking user {import_user['inputEmail']}")
                # check for each import user if there is an export user
                if any(import_user["inputEmail"] == export_user["username"] for export_user in export_list):
                    print(f"User already created and existent in export file")
                    continue
                else:
                    if not check_if_user_exists(import_user, fstl):
                        user_params = create_params_for_user(import_user, privileged_mapping_folder)
                        export_values = ["username", "password", "state"]
                        export_dict = {key: user_params[key] for key in export_values}
                        print(f"User does not exist and will be created: {export_dict}")
                        if fstl.create_user(user_params):
                            print(f"Creating User in Cyclos")
                    else:
                        export_dict = {"username": import_user["inputEmail"], "password": None, "state": "already exists"}
                        print(f"User already exists in cyclos, will be written to export file as {export_dict}")
                    export_list.append(export_dict)
                    with open(json_export_path, mode="w", encoding="utf-8") as json_file:
                        json.dump(export_list, json_file, indent=4, separators=(",", ": "))
    else:
        print(f"The file {json_export_path} does not exist!")
        with open(json_export_path, "w") as export_file_handler:
            export_list = []
            for import_user in import_data:
                if not check_if_user_exists(import_user, fstl):
                    user_params = create_params_for_user(import_user, privileged_mapping_folder)
                    export_values = ["username", "password", "state"]
                    export_dict = {key: user_params[key] for key in export_values}
                    print(f"User does not exist and will be created: {export_dict}")
                    if fstl.create_user(user_params):
                        print(f"Creating User in Cyclos")
                else:
                    export_dict = {"username": import_user["inputEmail"], "password": None, "state": "already exists"}
                    print(f"User already exists in cyclos, will be written to export file as {export_dict}")
                export_list.append(export_dict)
            json.dump(export_list, export_file_handler, indent=4, separators=(",", ": "))




def main():

    import_folder, export_folder, privileged_mapping_folder = get_folder_paths() 
    # check if improt and export folder exists at the given paths
    check_if_folder_exist(import_folder)
    check_if_folder_exist(export_folder)
    check_if_folder_exist(privileged_mapping_folder)

    FSTL_CYCLOS_ADMIN_USERNAME, FSTL_CYCLOS_ADMIN_PASSWORD = get_api_credentials()
    print("Initializing API to interact with Cyclos FSTL Community.")
    fstl = fstl_api(FSTL_CYCLOS_ADMIN_USERNAME, FSTL_CYCLOS_ADMIN_PASSWORD)
    
    # Iterate over all the files in the import directorz
    for filename in os.listdir(import_folder):
        file_path = os.path.join(import_folder, filename)
        # Ensure that it's a file and not a sub-directory
        if os.path.isfile(file_path):
            sync_users_for_single_file(file_path, fstl, privileged_mapping_folder)


if __name__ == "__main__":
    main()
