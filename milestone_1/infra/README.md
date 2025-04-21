
## Install stack steps

### Working directory
```
~/milestone_1/infr

```
### Prerequisite setup infra

Check for caller identity and make sure aws configure is correct
```
aws sts get-caller-identity

note: user "aws configure" if not correct
```
Set virtual environment for 'infra'
```
python -m venv .venv
```
Activate virtual environment for 'infra'
```
source .venv/bin/activate
```
Install required dependencies for 'infra'
```
pip install -r requirements.txt
```

### Configure for infra
Below configuration (**config.yml**) file will be updated **before/after** stack execution **manually** on each step of stack installation
```
~/milestore_1/infra/config.yml
```

## Step by step stack installation
### Step-1
First stack is to run, ParameterStack; which doesn't have any dependency to initiate need to update below propeties in **config.yml** with ParameteStack output

> **Before Execution** <br>
> NA
```
cdk deploy ParameterStack
```
> **After Execution** <br>
> parameter.arn.secret_store <br>
> parameter.arn.parameter_store 


### Step-2
Second stack is to run, CognitoStack; which need some static information before execution and update with result value after execution

> **Before Execution** <br>
> cognito.function.restrict_domain_name <br>
> cognito.user_pool.name <br>
> cognito.user_pool.region  <br>
> cognito.app_client.name
```
cdk deploy CognitoStack
```
> **After Execution** <br>
> frontend.cognito.user_pool.id <br>
> frontend.cognito.user_pool.region <br>
> frontend.cognito.app_client.id


### Step-3
Third stack is to run, BackendStack; which need service name and previous set parameter attributes before and returns service url; after execution. \
*~ already updated in previous stack*

> **Before Execution** <br>
> backend.service.name <br>
> ~ parameter.arn.secret_store <br>
> ~ parameter.arn.parameter_store 

```
cdk deploy BackendStack
```
> **After Execution** <br>
> backend.url

### Step-4
Fourth stack is to run, FrontendStack; which need backend url and cognito informations before and returns url after execution. \
*~ already updated in previous stack*

> **Before Execution** <br>
> backend.url <br>
> ~ frontend.cognito.user_pool.id <br>
> ~ frontend.cognito.user_pool.region <br>
> ~ frontend.cognito.app_client.id
```
cdk deploy FrontendStack
```
> **After Execution** <br>
> frontend.url

### Step-5
Fifth stack is to re-run, BackendStack; which need frontend url before and returns url after execution . \
*~ already updated in previous stack*

> **Before Execution** <br>
> ~ frontend.url
```
cdk deploy BackendStack
```
> **After Execution** <br>
> NA
