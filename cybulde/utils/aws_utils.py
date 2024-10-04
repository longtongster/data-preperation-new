# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/

import json

import boto3

from botocore.exceptions import ClientError


def get_secret() -> str:
    print("Extracting the github token from secrets manager")
    secret_name = "sachas_secret"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response["SecretString"]

    # Extract the value from the key
    secret_value: str = json.loads(secret)["github_token"]
    print(f"Github token retreived {secret_value}")

    return secret_value


if __name__ == "__main__":
    print(get_secret())
