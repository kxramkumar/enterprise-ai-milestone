import json
import boto3
import cognitojwt
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from utils.helper import Config

region = Config.get("cognito.region")
user_pool_id = Config.get("cognito.user_pool.id")
parameter_arn_secret_store = Config.get("parameter.arn.secret_store")
parameter_arn_parameter_store = Config.get("parameter.arn.parameter_store")
frontend_url = Config.get("frontend.url")

app = FastAPI()
# Allow all origins (for development purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_secret_by_arn(secret_arn, region_name="us-east-1"):
    client = boto3.client("secretsmanager", region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_arn)

        if "SecretString" in response:
            return json.loads(response["SecretString"])
        return response["SecretBinary"]
    except Exception as e:
        print(f"Error fetching secret: {e}")
        return None


def get_parameter_by_arn(parameter_arn, region_name="us-east-1", with_decryption=True):
    client = boto3.client("ssm", region_name=region_name)

    try:
        response = client.get_parameter(
            Name=parameter_arn, WithDecryption=with_decryption
        )
        return response["Parameter"]["Value"]
    except Exception as e:
        print(f"Error fetching parameter: {e}")
        return None


parameter_store_message = get_parameter_by_arn(parameter_arn_parameter_store)
secret_store_message = get_secret_by_arn(parameter_arn_secret_store)["message"]


# unprotected endpoint
@app.get("/")
async def home():
    return "Welcome to the home page!"


# unprotected endpoint
@app.get("/health")
async def health():
    return {
        "status": "All is well! Be Happy!",
        "message": parameter_store_message,
    }


@app.get("/refresh")
async def refresh():
    global secret_store_message
    global parameter_store_message
    parameter_store_message = get_parameter_by_arn(parameter_arn_parameter_store)
    secret_store_message = get_secret_by_arn(parameter_arn_secret_store)["message"]

    return {
        "status": "Successful! Refreshed parameter and secret messages",
    }


# protected endpoint
@app.get("/protected")
async def protected(request: Request):
    # let's look at the headers
    print(request.headers)

    # we extract the Authorization header
    authorization = request.headers.get("Authorization")
    print(authorization)

    # extract the token from the header
    token = authorization.split(" ")[1]
    # print(token)
    # print(region)
    # print(user_pool_id)
    # we use a library to decode and verify the token
    verified_claims = cognitojwt.decode(
        token=token,
        region=region,
        userpool_id=user_pool_id,
    )

    print("Extracted claims")
    print(verified_claims)
    return secret_store_message
