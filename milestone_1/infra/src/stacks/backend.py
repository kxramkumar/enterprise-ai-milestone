import os
from pathlib import Path
import time
from constructs import Construct
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_iam as iam
import cdk_ecr_deployment as ecr_deploy
from aws_cdk import Stack, CfnOutput
from aws_cdk import aws_apprunner as apprunner
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import RemovalPolicy, Aws

from utils.helper import Config


class BackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        app_name = Config.get("backend.service.name")
        # Step 1:
        # We need a ECR Repo
        backend_repo = self._create_ecr_repo()

        # Output the repository URI
        _ = CfnOutput(self, "BackendRepoUri", value=backend_repo.repository_uri)

        # Step 2:
        # Build the docker image
        image = self._create_docker_image()
        target_docker_image = (
            f"{Aws.ACCOUNT_ID}.dkr.ecr.{Aws.REGION}.amazonaws.com/{app_name}:latest"
        )

        # Step 3:
        # Push the docker image to ECR
        _ = ecr_deploy.ECRDeployment(
            self,
            "deploy-docker-image",
            src=ecr_deploy.DockerImageName(image.image_uri),
            dest=ecr_deploy.DockerImageName(target_docker_image),
        )

        # Step 4:
        # Create a role that can access ECR
        app_runner_access_role = self._create_apprunner_access_role()
        app_runner_instance_role = self._create_apprunner_instance_role()

        # Step 5:
        app_runner = self._create_app_runner(
            app_runner_access_role,
            app_runner_instance_role,
            target_docker_image,
        )

        CfnOutput(
            self,
            "BackendAppUrl",
            value=f"https://{app_runner.attr_service_url}",
            description="Backend application URL",
        )
        CfnOutput(
            self,
            "BackendImageUrl",
            value=image.image_uri,
            description="Backend image registry URLty",
        )

    def _create_ecr_repo(self):
        app_name = Config.get("backend.service.name")
        repository = ecr.Repository(
            self,
            "backend-repo",
            repository_name=app_name,
            image_scan_on_push=True,
            removal_policy=RemovalPolicy.DESTROY,
            empty_on_delete=True,
        )

        return repository

    def _create_docker_image(self) -> ecr_assets.DockerImageAsset:
        path_to_docker_dir = Path(os.getcwd()).parent.joinpath("backend/python")
        asset = ecr_assets.DockerImageAsset(
            self,
            "backend-app-image",
            directory=str(path_to_docker_dir),
            file="Dockerfile",
            asset_name="backend-app-image",
            platform=ecr_assets.Platform.LINUX_AMD64,
            cache_disabled=True,
        )
        return asset

    def _create_apprunner_access_role(self) -> iam.Role:
        app_name = Config.get("backend.service.name")
        role = iam.Role(
            self,
            "access-role",
            assumed_by=iam.ServicePrincipal("build.apprunner.amazonaws.com"),
            inline_policies={
                "access-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "ecr:GetAuthorizationToken",
                            ],
                            resources=["*"],
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "ecr:BatchCheckLayerAvailability",
                                "ecr:GetDownloadUrlForLayer",
                                "ecr:GetRepositoryPolicy",
                                "ecr:DescribeRepositories",
                                "ecr:ListImages",
                                "ecr:DescribeImages",
                                "ecr:BatchGetImage",
                                "ecr:GetLifecyclePolicy",
                                "ecr:GetLifecyclePolicyPreview",
                                "ecr:ListTagsForResource",
                                "ecr:DescribeImageScanFindings",
                            ],
                            resources=[
                                f"arn:aws:ecr:{Aws.REGION}:{Aws.ACCOUNT_ID}:repository/{app_name}"
                            ],
                        ),
                    ]
                )
            },
        )

        return role

    def _create_apprunner_instance_role(self) -> iam.Role:
        role = iam.Role(
            self,
            "instance-role",
            assumed_by=iam.ServicePrincipal("tasks.apprunner.amazonaws.com"),
            inline_policies={
                "instance-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "secretsmanager:GetResourcePolicy",
                                "secretsmanager:GetSecretValue",
                                "secretsmanager:DescribeSecret",
                                "secretsmanager:ListSecretVersionIds",
                            ],
                            resources=[
                                f"arn:aws:secretsmanager:{Aws.REGION}:{Aws.ACCOUNT_ID}:secret:*"
                            ],
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "secretsmanager:ListSecrets",
                            ],
                            resources=["*"],
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "ssm:GetParameter",
                                "ssm:GetParameters",
                            ],
                            resources=[
                                f"arn:aws:ssm:{Aws.REGION}:{Aws.ACCOUNT_ID}:parameter/*"
                            ],
                        ),
                    ]
                )
            },
        )

        return role

    def _create_app_runner(
        self,
        app_runner_access_role: iam.Role,
        app_runner_instance_role: iam.Role,
        target_docker_image: str,
    ):
        frontend_url = Config.get("frontend.url")
        secret_store_arn = Config.get("parameter.arn.secret_store")
        parameter_store_arn = Config.get("parameter.arn.parameter_store")
        service = apprunner.CfnService(
            self,
            "backend-service",
            service_name="ms1-backend",
            instance_configuration=apprunner.CfnService.InstanceConfigurationProperty(
                instance_role_arn=app_runner_instance_role.role_arn,
            ),
            source_configuration=apprunner.CfnService.SourceConfigurationProperty(
                authentication_configuration=apprunner.CfnService.AuthenticationConfigurationProperty(
                    access_role_arn=app_runner_access_role.role_arn,
                ),
                image_repository=apprunner.CfnService.ImageRepositoryProperty(
                    image_identifier=target_docker_image,
                    image_repository_type="ECR",
                    image_configuration=apprunner.CfnService.ImageConfigurationProperty(
                        port="8000",
                        runtime_environment_variables=[
                            apprunner.CfnService.KeyValuePairProperty(
                                name="FRONTEND_URL",
                                value=frontend_url,
                            ),
                            apprunner.CfnService.KeyValuePairProperty(
                                name="PARAMETER_ARN_PARAMETER_STORE",
                                value=parameter_store_arn,
                            ),
                            apprunner.CfnService.KeyValuePairProperty(
                                name="PARAMETER_ARN_SECRET_STORE",
                                value=secret_store_arn,
                            ),
                            # Below is a hack to redeploy apprunner. where adding Dummy variable to
                            # trigger redeploy
                            # NOTE: Correct way is to create Unique tag (v1, v2) for
                            apprunner.CfnService.KeyValuePairProperty(
                                name="FORCE_DEPLOY_TOKEN",  # Dummy var to trigger redeploy
                                value=str(int(time.time())),  # Changes on every deploy
                            ),
                        ],
                        # runtime_environment_secrets=[
                        #     apprunner.CfnService.KeyValuePairProperty(
                        #         name="PARAMETER_ARN_PARAMETER_STORE",
                        #         value=parameter_store_arn,
                        #     ),
                        #     apprunner.CfnService.KeyValuePairProperty(
                        #         name="PARAMETER_ARN_SECRET_STORE",
                        #         value=secret_store_arn,
                        #     ),
                        # ],
                    ),
                ),
                auto_deployments_enabled=True,
            ),
            health_check_configuration=apprunner.CfnService.HealthCheckConfigurationProperty(
                path="/health",
                protocol="HTTP",
            ),
        )

        return service
