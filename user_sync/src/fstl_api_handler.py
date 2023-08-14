import requests
from requests.auth import HTTPBasicAuth
import json


class fstl_api:
    """
    Class to interact with the Cyclos API
    Only very few functions of the API are used
    the API URI of the cyclos community is hard coded as a default value
    however, can be overwritten by passing another URI
    for API reference see: https://communities.cyclos.org/fstl/api
    """

    def __init__(
        self,
        username: str,
        password: str,
        url: str = "https://communities.cyclos.org/fstl/api",
    ) -> None:
        """
        :param url: URL of the the API
        :param username: name of the user to authenticate with
        :param password: password of this user
        """
        self.url = url
        self.username = username
        self.password = password
        self.verify = True
        # Cyclos API uses Basic Auth
        # HTTPBasicAuth adds base64-decoded "username:password"
        # to the header of the API request
        self.auth = HTTPBasicAuth(self.username, self.password)
        self.headers = {"Accept": "application/json"}

    def get_brokers_of_user(self, user: str):
        """
        get all brokers of an user account
        :param user: the user to get the brokers from
        :return: if succes: json object with the brokes, else: False
        """
        response = requests.get(
            f"{self.url}/{user}/brokers",
            headers=self.headers,
            auth=self.auth,
            verify=self.verify,
        )
        if evaluate_response(response):
            return json.loads(response.content)
        else:
            return evaluate_response(response)

    def get_users(
        self, group: list = [""], role: list = [""], status: list = ["active"]
    ):
        """
        get all user accounts
        :param group: only get users in the given groups
        :param role: only get users with the given roles
        :param status: only get user with the given stati
        :return: if succes: json object with the users, else: False
        """
        params = {
            "addressResult": "none",  # we don't need adresses here
            "roles": role,
            "statuses": status,
            "groups": group,
        }
        response = requests.get(
            f"{self.url}/users",
            params=params,
            headers=self.headers,
            auth=self.auth,
            verify=self.verify,
        )
        if evaluate_response(response):
            return json.loads(response.content)
        else:
            return evaluate_response(response)

    def check_if_user_exists(self, check_string: str = ""):
        users = self.get_users()
        print(users)
        if any(user_item["display"] == check_string for user_item in users):
            return True
        else:
            return False

    def create_user(self, params: dict):
        """
        create a new user account
        :param name: the name
        :param username: the username
        :param email: the mail
        :param group: the group of the user
        :return: if succes: json object with the users, else: False
        """
        print(params)
        data = {
            "name": params["name"],
            "username": params["username"],
            "email": params["email"],
            "customValues": { },
            "group": params["group"],
            "passwords": [
                {
                    "type": "login",
                    "value": params["password"],
                }
            ],
        }
        if "sorgeberechtigte" in params:
            data["customValues"]["sorgeberechtigte"] = params["sorgeberechtigte"]
        if "kinder" in params:
            data["customValues"]["kinder"] = params["kinder"]
        response = requests.post(
            f"{self.url}/users",
            json=data,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            auth=self.auth,
            verify=self.verify,
        )
        print(response.content)
        return evaluate_response(response)

    def add_broker_to_user(
        self, user: str, broker: str, main_broker: bool = False
    ) -> bool:
        """
        add a broker to a user account
        :param user: the user to add the broker to, id or display name are valid
        :param broker: the broker to add to the user, id or display name are valid
        :param main_broker: is the broker the main broker?
        :return: Boolean to indicate success of operation
        """
        data = {"main": main_broker}
        response = requests.post(
            f"{self.url}/{user}/brokers/{broker}",
            data=data,
            headers={"Accept": "*/*"},
            auth=self.auth,
            verify=self.verify,
        )
        return evaluate_response(response)

    def delete_broker_from_user(self, user: str, broker: str) -> bool:
        """
        delete a broker from a user account
        :param user: the user to remove the broker from, id or display name are valid
        :param broker: the broker to remove from the user, id or display name are valid
        :return: Boolean to indicate success of operation
        """
        response = requests.delete(
            f"{self.url}/{user}/brokers/{broker}",
            headers=self.headers,
            auth=self.auth,
            verify=self.verify,
        )
        return evaluate_response(response)

    def get_balance_of_users(self):
        response = requests.get(
            f"{self.url}/accounts/user/user-balances",
            headers=self.headers,
            auth=self.auth,
            verify=self.verify,
        )
        if evaluate_response(response):
            return json.loads(response.content)
        else:
            return evaluate_response(response)

    def make_system_payment_to_user(self, user: str, amount: float):
        pass

    def get_data_for_system_payment_to_user(self, user: str):
        # curl -X GET "https://communities.cyclos.org/fstl/api/system/payments/data-for-perform?to=7762070814191090239"
        pass


def evaluate_response(response) -> bool:
    """
    evaluates the response of an API call
    :param response: the response of the API call to evaluate
    :return: True if ok (200 < status code < 300), False if not
    """
    if 200 <= response.status_code < 300:
        return True
    else:
        return False
