## Run Backend application steps

### Working directory
```
~/milestore_1/backend/python
```
### Prerequisite setup infra

Check for caller identity and make sure aws configure is correct
```
aws sts get-caller-identity

note: user "aws configure" if not correct
```
Set virtual environment for 'backend/python'
```
python -m venv .venv
```
Activate virtual environment for 'backend/python'
```
source .venv/bin/activate
```
Install required dependencies for 'backend/python'
```
pip install -r requirements.txt
```

**Note: \
ParameterStack is needed for Local, LocalContainer or AppRunner run/deployments.**

### Run locally
When application run locally; required properties are feeded from config.yml
> Note: Need to set below properties in **config.yml**<br>
> cognito.region <br>
> cognito.user_pool.id <br>
> frontend.url <br>
> parameter.arn.parameter_store <br>
> parameter.arn.secret_store <br>
```
fastapi dev src/service.py
```
### Run in LocalContainer
```
Note:
Need to set below environment in Dockerfile.local before initial docker build

ENV APP_CONFIG_PATH=/project/backend/config.yml
ENV AWS_ACCESS_KEY_ID=<access_key_id>
ENV AWS_SECRET_ACCESS_KEY=<secret_key>
ENV AWS_REGION=<region>

docker build -f Dockerfile.local -t ms1-backend-local .
docker run --rm -p 8000:8000 ms1-backend-local
```

### Run in AppRunner
Note:
Here all properties are updated in environment itself 
(eg. frontend.url -> FRONTEND_URL )
```
use 'Dockerfile' in BackendStack
```

### Note
```
Need use 'APP_CONFIG_PATH' in environmental variable (eg: export APP_CONFIG_PATH=config.yml) if working directory is changed.
```
```
'utils/helper.py' has 'Config' class which is capable of reading from 'config.yml' same time it override value from environments
```
```
CORS is enabled to allow frontend to access api.
allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
```