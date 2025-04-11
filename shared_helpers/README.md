# Using Shared Python Package

Steps:
1. Create a Shared Package:

Create a new folder, e.g., shared_helpers, at the root of your project.
Move all shared helper functions (e.g., gen_boto3_client, safeget, etc.) into this folder.
Add a setup.py or pyproject.toml file to make it an installable Python package.

Example structure:

shared_helpers/
├── shared_helpers/
│   ├── __init__.py
│   ├── boto3_helpers.py
│   ├── utils.py
├── setup.py

Install the Package:

2. Use pip install -e ./shared_helpers to install the package locally in both shared and helpers.
Update Imports:

3. Update your imports in both shared and helpers to use the shared package:

`from shared_helpers.boto3_helpers import gen_boto3_client`

Advantages:
Centralized management of shared code.
Easy to update and version the shared helpers.
Avoids duplication of code across folders.

. Use Lambda Layers
Another option is to package shared_helpers as a Lambda Layer. This allows you to share the dependency across multiple functions.

Steps:
Create a shared_helpers directory and install the dependency:

Publish the layer:

Reference the layer in your serverless.yml file:
```
functions:
  s3_bulkimg_analyse:
    handler: functions.func_s3_bulkimg_analyse.run
    layers:
      - arn:aws:lambda:${self:provider.region}:${aws:accountId}:layer:shared_helpers:1
```

Summary of Solutions
Best Option: Package shared_helpers as a Python package and install it via pip.
Quick Fix: Include shared_helpers in the deployment package using the include option in serverless.yml.
Alternative: Disable dockerizePip (may cause compatibility issues).
Advanced: Use Lambda Layers to share shared_helpers across functions.
Choose the solution that best fits your project's requirements. Packaging shared_helpers as a Python package is the most robust and maintainable approach.
