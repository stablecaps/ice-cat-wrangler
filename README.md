# ice-cat-wrangler

## Context

In this task, we ask you to prepare a simple service that, for a given image file (JPEG/PNG), answers the question: **Does the image file contain the image of a cat?**

**Problem**
- **Does the image file provided contain a cat?**

**Input**
- Picture file (JPG/PNG)

**Output**
- Yes or No

---

## Task Requirements

We need the following behaviors:

1. User can upload an image file for scanning.
2. User can only upload JPEG and PNG files.
3. The image is kept in persistent storage.
4. Scanning is a non-blocking operation.
5. User can check the result of image scanning.
6. Results are kept in persistent storage.
7. Debug data is available for a power user.
8. There is any kind of interface available to interact with the application.

---

## Extra Information

1. Only consider **AWS cloud** and AWS/Amazon services.
2. Build a **serverless application**.
3. Use any high-level programming language.
4. You are free to choose the build tools, libraries, etc.
5. Ensure that the code in the submission is fully functional and include instructions for building and running it.
6. You don't need to dedicate days to this; simply demonstrate your ability to craft excellent software.
7. Use this exercise as a guide for design decisions, considering it as the initial prototype of a Minimum Viable Product (MVP) that will evolve into a production-ready deliverable.
8. Be prepared for further discussions regarding how to transition and scale the prototype for future deployment.

---

# Solution Overview:

I've tried to write code that sets-up avenues whereby we can minimise cost whilst maximising performance. Obviously, this is an iterative process that materialises results as the requirements crystalise.

The repository is divided into 3 major components:
1. infra-terra: contains terraform code to create various AWS resources
2. serverless: contains a lambda function that handles image processing
3. shared_helpers: contains shared functions and classes that can be shared between infra-terra and serverless. I've tried to write the code to be easily abstractable to other use cases. That way it could potentially be split out into a separate repo so that other applications can also use this code.

The solution relies upon using both terraform and serverless as deployment agents for the following reasons as each tool has its strengths & weaknesses.

1. **Serverless**:
    - Ideal for deploying Lambdas and API Gateways.
    - `sls deploy` uses easily definable configurations from the `serverless.yml` file.
    - Requires less code to deploy things such as an API Gateway compared to Terraform.
    - Resources are tightly coupled to application code changes.
    - Allows developers to deploy without requiring specialized DevOps knowledge.

#### Resources are shared between terraform and serverless using SSM variables. The api-client also leverages the same SSM variables to auto-configure resource env vars.

2. **Terraform**:
    - Is good to deploy more fundamental resources such as s3 buckets, iam policies, etc because
    - It is less code in some cases. (have you seen an IAM policy in serverless.yml?)
    - The terraform deployment role in most companies ends up getting more & more permissions added to it till it usually converges to administrator. Allowing many devs to have admin access is a security issue. Thus, things like IAM, route43, etc should be restricted.
    - As we would like to promote between identical dev --> uat --> prod stages, it would make sense to let devs create the app in dev as it would be deployed in prod.


For more details on the co-location method used here please see: [Terraform & Serverless Co-location Demo](https://github.com/stablecaps/terraform_and_serverless_demo)

The article also discusses other aspects such as how to best organise terraform repos, etc.


---

## Setup

**Setup assumes you have AWS admin credentials and can export them into your terminal environment**

### Installation order
1. Terraform
2. Serverless
3. Api-client

---

1. Terraform




- **Pre-commit setup**
- **S3 lifecycle**: Delete old objects (14 days).
- **DynamoDB (DDB)**:
  - TTL to delete old entries (14 days).
  - Autoscaling to handle load.
- **Lambda alerts**.
- Handle deletion of items from the bucket: Delete corresponding entries from DynamoDB.

---
## Axioms for S3 Design

1. s3 performance: https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html
    * multiple prefixes
    * multiple client connections
    * handle 503 slowdown messages
    * check requests are being spread over a wide pool of Amazon S3 IP addresses
    * if using cloudfront - check s3 transfer acceleration
2. s3 naming: https://aws.amazon.com/blogs/big-data/building-and-maintaining-an-amazon-s3-metadata-index-without-servers/
    * name with high cardinality for performance


### [Click for Detailed Design S3 keys](docs/design_s3_key_naming.md)

---

## Axioms for DB Design

1. The image is kept in persistent storage.
2. Scanning is a non-blocking operation:
   - Results cannot be returned in the same POST call.
   - A results endpoint is needed (should handle single and batch image submission results).
3. User can check the result of image scanning:
   - Assume this check can be performed at any time.
   - The client stores a record of:
     - `batch_id`
     - `original_file_name`
     - `upload_time="YYYY-MM-DD-HH"`
     - `file_image_hash`
     - `epoch_timestamp`
   - For the database:
     - Multiple clients/customers should have unique IDs to assist with searching.

### [Click for Detailed Design DynamoDB](docs/design_dynamodb.md)

---

## Backend Design (S3 & DynamoDB)

### Workflow

1. **User uploads an image** to `s3bucketSource` → triggers a Lambda function.
2. Lambda:
   - Submits the image to Amazon Rekognition (writes a DynamoDB record).
   - Gets the Rekognition response (updates DynamoDB).
   - On success:
     - Moves the image to `s3bucketDest` (updates DynamoDB).
   - On failure:
     - Moves the image to `s3bucketFail` (updates DynamoDB).

### Additional Notes

1. Save the hash of the file to avoid reprocessing.
2. Uniquely rename the file to prevent filename clashes in S3 (use the hash).

---

## DynamoDB Entries

| Field         | Type   | Description                                                                 |
|---------------|--------|-----------------------------------------------------------------------------|
| `<PK>`        | int    | `upload_id` - Groups images batch uploaded (for batch retrieval).          |
| `<SK>`        | str    | `img_key` - Bucket location (updated with renaming process).               |
| `img_fprint`  | str    | Hash of the image file.                                                    |
| `op_status`   | str    | Operation status (`pending`, `success`, `fail`).                           |
| `rek_resp`    | json   | Rekognition response as JSON.                                              |
| `rek_iscat`   | bool   | Whether the image contains a cat.                                          |
| `logs`        | json   | Debug logs for retrieval.                                                  |
| `upload_ts`   | datetime | Timestamp of the upload.                                                 |
| `rek_ts`      | datetime | Timestamp of the Rekognition response.                                   |

---

## DynamoDB Use Cases

1. Track image processing status.
2. Track Rekognition response (is it a cat?).
3. Track image location/filename (source, destination, failure).
4. Track image hash (to avoid reprocessing).
5. Track logs associated with each submission.

---

## S3 Upload Filename Format

```plaintext
${file_hash}/${mach_host_name}-${YYYY-MM-DD-HH-MM}/${USERID}-${epoch_timestamp}.png


1. s3 performance: https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html
    * multiple prefixes
    * multiple client connections
    * handle 503 slowdown messages
    * check requests are being spread over a wide pool of Amazon S3 IP addresses
    * if using cloudfront - check s3 transfer acceleration
2. s3 naming: https://aws.amazon.com/blogs/big-data/building-and-maintaining-an-amazon-s3-metadata-index-without-servers/
    * name with high cardinality for performance
3. dynamodb: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-use-s3-too.html
    * 400kb limit per item. utilize the ReturnConsumedCapacity parameter
    * compress large attribute values
    * object metadata support in Amazon S3 to provide a link back to the parent item in DynamoDB
