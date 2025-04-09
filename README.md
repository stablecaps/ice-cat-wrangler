# ice-cat-wrangler


setup pre-commit

s3 lifecycle - delete old objects (14 days)
DDB - ttl delete old entries (14 days)
DDB - autoscaling to handle  load
lambda alerts

handle delete item from bucket - dlete from DDB as well

## Axioms for DB design
1. the image is kept in a persistent storage
2. scanning is non-blocking operation
    - Therefore we cannot return results in same post call
    - need a results endpoint (should be able to handle single & batch image submission results)
3. user can check result of image scanning
    - assume that this check can be performed at anytime
    - therefore upload_id should be stored with timestamp in client
    - client should also store image hash and filename
    - for the db: as there could be multiple clients/customers - it would probably be better for each client to have a unique id to assist searching


## Backend design (S3 & DynamoDB):
user -> uploads image to s3bucketSource -> this.lambda
    1. submits image to rekognition (write DynDB record)
    2. gets rekognition response (update DynDB)
    3. success -> moves image to s3bucketDest (update DynDB)
    4. failure -> moves image to s3bucketFail (update DynDB)

Additional notes:
    1. Save hash of file to avoid reprocessing
    2. uniquely rename file to prevent filename clashes in s3 (use hash)


DynamoDB entries:
    3. [str] <SK> img_key in bucket location (will be updated with any renaming process) begins with
    2. [int] <PK> upload_id - to group images batch uploaded (for batch retrieval)
    1. [str] img_fprint
    4. [str] op_status (pending, success, fail)
    5. [json] rek_resp as json
    6. [bool] rek_iscat: is image a cat?
    7. [json] logs for debug retrieval?
    8. [datetime] upload_ts
    9. [datetime] rek_ts

DDB use cases (can be single or batch):
    1. track image processing status
    2. track rekognition response (is a cat?)
    3. track image location/filename (source, dest, fail)
    4. track image hash (to avoid reprocessing) (is the main key)
    5. track logs associated with each submission


s3_upload_filename = ${file_hash}/${mach_host_name}-${YYYY-MM-DD-HH-MM}/${USERID}-${epoch timestamp}.png

So retrive a single entry or retrive a batch of entries
    1. Find all objects for a given upload_id collected during a time range


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
