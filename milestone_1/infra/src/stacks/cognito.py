import os
import pystache
import subprocess
from pathlib import Path
from utils.helper import Config
from constructs import Construct
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_iam as iam
from aws_cdk import aws_cloudfront as cf
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_cognito as cognito

from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_s3_deployment as s3_deployment
from aws_cdk import Fn, Stack, RemovalPolicy, CfnOutput
from aws_cdk import aws_lambda_python_alpha as lambda_python


class CognitoStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get user pool name from config
        user_pool_name = Config.get("cognito.user_pool.name")
        # Get app client name from config
        app_client_name = Config.get("cognito.app_client.name")
        # Get restrict domain function name from config
        function_name = Config.get("cognito.function.restrict_domain.name")
        function_path = Path(os.getcwd()).parent.joinpath("function/restrict_domain")

        # print(function_path)
        domain_restrict_lambda = lambda_python.PythonFunction(
            self,
            function_name,
            description="Function is to restrict external users to user pool; allow only hidglobal/assaabloy users.",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_handler",
            index="main.py",
            entry=str(function_path),
        )

        # Grant Cognito permission to invoke the Lambda function
        domain_restrict_lambda.add_permission(
            "CognitoInvokeLambda",
            principal=iam.ServicePrincipal("cognito-idp.amazonaws.com"),
            action="lambda:InvokeFunction",
        )

        # Creating user pool
        user_pool = cognito.UserPool(
            self,
            user_pool_name,
            user_pool_name=user_pool_name,
            password_policy=cognito.PasswordPolicy(
                min_length=6,
                require_digits=False,
                require_lowercase=False,
                require_uppercase=False,
                require_symbols=False,
            ),
            mfa=cognito.Mfa.OFF,
            sign_in_aliases=cognito.SignInAliases(email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True),
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            self_sign_up_enabled=True,
            removal_policy=RemovalPolicy.DESTROY,
            lambda_triggers=cognito.UserPoolTriggers(
                pre_sign_up=domain_restrict_lambda
            ),
        )

        # Creating app client and attach to user pool
        app_client = user_pool.add_client(
            app_client_name,
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
            ),
        )

        user_pool_id = user_pool.user_pool_id
        user_pool_region = Fn.select(3, Fn.split(":", user_pool.user_pool_arn))
        app_client_id = app_client.user_pool_client_id

        _ = CfnOutput(
            self,
            "UserPoolId",
            value=user_pool_id,
            description="User pool ID, generated on deployment",
            export_name="cognito-user-pool-id",
        )

        _ = CfnOutput(
            self,
            "UserPoolRegion",
            value=user_pool_region,
            description="User pool region where it created",
            export_name="cognito-user-pool-region",
        )

        _ = CfnOutput(
            self,
            "AppClientId",
            value=app_client_id,
            description="App client ID of the user pool client",
            export_name="cognito-app-client-id",
        )

        _ = CfnOutput(
            self,
            "DomainRestrictLambdaARN",
            value=domain_restrict_lambda.function_arn,
            description="ARN of the domain restrict lambda function",
            export_name="cognito-domain-restrict-lambda-arn",
        )
