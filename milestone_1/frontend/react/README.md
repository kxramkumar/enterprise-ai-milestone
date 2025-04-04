## Run Frontend application steps

### Working directory
```
~/milestore_1/frontend/react
```

### Prerequisite setup infra
```
npm create vite@latest . --template react-ts
npm install react-router-dom @aws-amplify/auth @aws-amplify/ui-react
```
```
Note: Update vite.config.ts file with port and host information
 server: {
    port: 5173,
    host: "0.0.0.0",
  },
```
*src/assets/app-config.ts* and *src/assets/aws-config.ts* which is used by application. \

**Note: \
CognitoStack is needed for either Local or S3 run/deployments.**

### Run locally
Note: *app-config.ts* and *aws-config.ts* should be placed in *src/assets folder* with local configuration before running the application.
```
npm run dev
```

### Host in S3
Note:
Here both files *ap-config.ts* and *aws-config.ts* are created in FrontendStack with appropriate information
```
using FrontendStack
```
