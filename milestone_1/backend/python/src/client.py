import requests
from utils.helper import Config


_USERNAME = "kxramkumar@gmail.com"
_PASSWORD = "password1234"
_COGNITO_CLIENT_ID = Config.get("cognito.user_pool.client.id")
_URL = "https://cognito-idp.us-east-1.amazonaws.com/"
_HEADERS = {
    "Content-Type": "application/x-amz-json-1.1",
    "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth",
}

_DATA = {
    "AuthParameters": {
        "USERNAME": _USERNAME,
        "PASSWORD": _PASSWORD,
    },
    "AuthFlow": "USER_PASSWORD_AUTH",
    "ClientId": _COGNITO_CLIENT_ID,
}


def get_id_token() -> str:
    response = requests.post(url=_URL, headers=_HEADERS, json=_DATA)
    print(response.json())
    response_data = response.json()["AuthenticationResult"]

    id_token = response_data["IdToken"]
    access_token = response_data["AccessToken"]

    print("## Id Token")
    print(id_token)

    # print("## Access Token")
    print(access_token)

    return id_token


def make_protected_request():
    id_token = get_id_token()

    response = requests.get(
        url="http://localhost:8000/protected",
        headers={"Authorization": f"Bearer {id_token}"},
    )

    print(response)


if __name__ == "__main__":
    # get_id_token()
    make_protected_request()
