from aws_cdk import CfnOutput, Stack
from constructs import Construct
from aws_cdk import aws_ssm as ssm
from aws_cdk import aws_secretsmanager as secretsmanager


class ParameterStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Create an SSM Parameter
        parameter_store = ssm.StringParameter(
            self,
            "SSMParameter",
            parameter_name="/message/ms-1",
            string_value="Message from parameter store",
            description="Parameter message in milestone-1",
            tier=ssm.ParameterTier.STANDARD,
        )

        # Create a Secret in Secrets Manager
        secret_manager = secretsmanager.Secret(
            self,
            "SecretManager",
            secret_name="secret_message",
            description="Secret message in milestone-1",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"message": "secretmanager: If you are seeing this then you have authenticated correctly"}',
                generate_string_key="password",
            ),
        )

        _ = CfnOutput(
            self,
            "SSMParameterNameArn",
            value=parameter_store.parameter_arn,
            description="Messsage arn from parameter store",
        )

        _ = CfnOutput(
            self,
            "SecretManagerArn",
            value=secret_manager.secret_arn,
            description="Message arn from secret store",
        )
