## Milestone-1 Project


1. backend: /protected which gets message from secrets_manager after user authenticates
0. backend: /healthy which gets message from parameter_store
0. backend: hosted in AppRunner
0. frontend: using mustache to create aws-config.ts before building frontend
0. frontend: after login; frontend invoke /protected with authtoken to get secretmessage (CORS is enable in Backend, by specifying Frontend URL)
0. frontend: trigger pre-sign-up lamba function in cognito; while sign-up from UI it will restrict user other than hid/assaabloy domains


```
~/milestone_1/backend/python -> has backend implementation
~/milestone_1/frontend/react -> has react + vite + typescript implementation
~/milestone_1/function/restrict_domain/main.py -> has AWS lambda triggers on 'pre-sign-up' for restrict domain "@hidglobal.com", "@assaabloy.com"
~/milestone_1/infra/ -> all infra related implementations
     ~/milestone_1/infra/src/stacks/parameter.py -> Responsible to add values in parameter_store and secrets_manager (step-1)
     ~/milestone_1/infra/src/stacks/cogito.py -> It create user-pool, install pre-sign-up lambda and configure with user-pool, create app-client (step-2)
     ~/milestone_1/infra/src/stacks/backend.py -> Perform backend build docker, push to aws-ecr, deploy in app-runner (step-3 and re-run in step-5)
     ~/milestone_1/infra/src/stacks/frontend.py -> It build react-ui, push the artifacts to aws-s3 (step-4)
```
Kindly follow below README.md for respective projects,

[Backend application README](./milestone_1/backend/python/README.md); To run backend Local[^1], Local[^1] Docker or in AppRunner[^2]. \
[Frontend application README](./milestone_1/frontend/react/README.md); To run frontend Local[^1] and S3 deployment[^3] \
[Infrastructure README](./milestone_1/infra/README.md); To run CDK stacks, ParameterStack, CognitoStack, BackendStack, FrontendStack

> Note: \
> [^1] Local -> inside DevContainer \
> [^2] Before running backend; please make sure 'ParameterStack' is successful (cdk deploy ParameterStack) \
> [^3] Before running frontend; please make sure 'CognitoStack' is successful (cdk deply Cognito)

