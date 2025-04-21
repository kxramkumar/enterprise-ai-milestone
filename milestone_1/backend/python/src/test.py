import base64
import json
import boto3
from utils.helper import Config


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


backend_arn_parameter_store = Config.get("parameter.arn.parameter_store")
backend_arn_secret_store = Config.get("parameter.arn.secret_store")
print(backend_arn_parameter_store)
print(backend_arn_secret_store)
print(get_parameter_by_arn(backend_arn_parameter_store))
print(get_secret_by_arn(backend_arn_secret_store)["message"])
