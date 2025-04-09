# ice-cat-wrangler


setup pre-commit

## Backend design (S3 & DynamoDB):
user -> uploads image to s3bucketSource -> this.lambda
    1. submits image to rekognition (write DynDB record)
    2. gets rekognition response (update DynDB)
    3. success -> moves image to s3bucketDest (update DynDB)
    4. failure -> moves image to s3bucketFail (update DynDB)

Additional notes:
    1. Save hash of file to avoid reprocessing
    2. uniquely rename file to prevent filename clashes in s3 (use hash)

DDB use cases (can be single or batch):
    1. track image processing status
    2. track rekognition response (is a cat?)
    3. track image location/filename (source, dest, fail)
    4. track image hash (to avoid reprocessing) (is the main key)
    5. track logs associated with each submission

    * So retrive a single entry
    * Or retrive a batch of entries

DynamoDB entries:
    3. [str] <SK> image filename in bucket location (will be updated with any renaming process) begins with
    2. [int] <PK> upload batch id - to group images batch uploaded (for batch retrieval)
    1. [str] image hash
    4. [str] operation status (pending, success, fail)
    5. [json] rekognition response as json
    6. [bool] rekognition: is image a cat?
    7. [json] logs for debug retrieval?
    8. [datetime] upload timestamp
    9. [datetime] rekognition timestamp



1. s3 performance: https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html
    * multiple prefixes
    * multiple client connections
    * handle 503 slowdown messages
    * check requests are being spread over a wide pool of Amazon S3 IP addresses
    * if using cloudfront - check s3 transfer acceleration
