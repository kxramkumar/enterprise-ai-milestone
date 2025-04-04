import os
import pystache
import subprocess
from pathlib import Path
from aws_cdk import Stack
from constructs import Construct

from aws_cdk import CfnOutput, RemovalPolicy

from aws_cdk import aws_cloudfront as cf
from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3_deployment

from utils.helper import Config


class FrontendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get the intended region where this jobs runs

        project_region = Config.get("region")
        user_pool_id = Config.get("frontend.cognito.user_pool.id")
        user_pool_region = Config.get("frontend.cognito.user_pool.region")
        app_client_id = Config.get("frontend.cognito.app_client.id")
        backend_url = Config.get("backend.service.url")

        react_path = Path(os.getcwd()).parent.joinpath("frontend/react")
        data: dict[str, str] = {
            "project_region": project_region,
            "cognito_region": user_pool_region,
            "cognito_user_pool_id": user_pool_id,
            "cognito_user_pool_client_id": app_client_id,
            "backend_url": backend_url,
        }
        self._build_frontend(react_path, data)

        bucket = self._create_and_deploy_bucket(react_path)
        distribution = self._create_cloud_distribution(bucket)

        _ = CfnOutput(
            self,
            "FrontendStackProjectRegion",
            value=project_region,
            description="The project region",
        )
        _ = CfnOutput(
            self,
            "FrontendStackUserPoolId",
            value=user_pool_id,
            description="User pool ID, generated in cognito stack",
        )
        _ = CfnOutput(
            self,
            "FrontendStackUserPoolRegion",
            value=user_pool_region,
            description="User pool region, where cognito stack created",
        )
        _ = CfnOutput(
            self,
            "FrontendStackClientId",
            value=app_client_id,
            description="App client ID,  generated in cognito stack",
        )
        _ = CfnOutput(
            self,
            "FrontendDistributionDomainName",
            value=f"https://{distribution.distribution_domain_name}",
            description="Domain name of the CloudFront distribution",
        )

    def _build_frontend(self, front_end: Path, data: dict[str, str]) -> None:
        # Generate aws-exports.ts
        aws_exports_template = front_end.joinpath("src/assets/aws-exports.ts.prod")
        aws_exports_file = front_end.joinpath("src/assets/aws-exports.ts")
        with open(aws_exports_template, "r", encoding="utf-8") as file:
            template = file.read()
        rendered_content = pystache.Renderer().render(template, data)
        with open(aws_exports_file, "w", encoding="utf-8") as file:
            file.write(rendered_content)

        # Generate app-exports.ts
        app_exports_template = front_end.joinpath("src/assets/app-exports.ts.prod")
        app_exports_file = front_end.joinpath("src/assets/app-exports.ts")
        with open(app_exports_template, "r", encoding="utf-8") as file:
            template = file.read()
        rendered_content = pystache.Renderer().render(template, data)
        with open(app_exports_file, "w", encoding="utf-8") as file:
            file.write(rendered_content)

        # Build client application
        subprocess.run(["npm", "install"], cwd=str(front_end), check=True)
        subprocess.run(["npm", "run", "build"], cwd=str(front_end), check=True)

    def _create_and_deploy_bucket(self, react_path: Path) -> s3.Bucket:
        bucket_name = Config.get("frontend.bucket.name")

        web_bucket = s3.Bucket(
            self,
            "bucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
            block_public_access=s3.BlockPublicAccess.BLOCK_ACLS,
            public_read_access=True,
            website_index_document="index.html",
            website_error_document="index.html",
            bucket_name=bucket_name,
        )

        # Step 1b: Pushing the content of the frontend to the S3 bucket
        dist_dir_path = react_path / "dist"
        s3_deployment.BucketDeployment(
            self,
            "deployment",
            sources=[s3_deployment.Source.asset(str(dist_dir_path))],
            destination_bucket=web_bucket,
        )

        return web_bucket

    def _create_cloud_distribution(self, web_bucket) -> cf.Distribution:
        distribution = cf.Distribution(
            self,
            "distribution",
            default_root_object="index.html",
            default_behavior=cf.BehaviorOptions(
                origin=origins.S3StaticWebsiteOrigin(web_bucket)
            ),
        )

        return distribution
