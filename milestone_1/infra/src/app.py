import aws_cdk as cdk

from stacks.backend import BackendStack
from stacks.cognito import CognitoStack
from stacks.frontend import FrontendStack
from stacks.parameter import ParameterStack

app = cdk.App()

# Step:1
# After this stack completed update below properties in config.yml
# parameter.arn.secret_store
# parameter.arn.parameter_store

# parameterStack = ParameterStack(app, "ParameterStack")

# Step:2
# After this stack completed update below properties in config.yml
# frontend.cognito.user_pool.id
# frontend.cognito.user_pool.region
# frontend.cognito.app_client.id

# cognito_stack = CognitoStack(app, "CognitoStack")

# Step:3 (rerun without frontend.url; CORS is disabled)
# After this stack completed update below properties in config.yml
# backend.url
# Step:5 (rerun with frontend.url; To enable CORS for frontend)

backendStack = BackendStack(app, "BackendStack")

# Step:4
# After this stack completed update below properties in config.yml
# frontend.url

# frontendStack = FrontendStack(app, "FrontendStack")

app.synth()
