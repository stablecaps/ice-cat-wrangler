# S3 key naming considerations

The S3 backend partitions data based on the prefix of the object key. If many objects share the same prefix (e.g., `client_id`), it can lead to hot partitions. This is where a single partition is overloaded with requests. This is especially problematic if a single client_id uploads a large number of files in a short period.

Sequential Timestamps including YYYY-MM-DD-HH and epoch_timestamp in the key creates a sequential pattern. If many objects are uploaded in chronological order, this can result in S3 storing these objects in the same partition, further exacerbating hot partitioning.

## Optimising S3 performance:

1. Introduce Randomness in the Prefix: A random or hashed component at the beginning of the key distributes objects more evenly across partitions. Example: `random_prefix/client_id/file_hash-YYYY-MM-DD-HH/epoch_timestamp.png`.

2. Avoid Sequential Patterns: Avoid sequential timestamps (YYYY-MM-DD-HH or epoch_timestamp) in the prefix. Instead, place them later in the key or combine with a hash.

3. If we expect a high volume of uploads from a single `client_id`, consider using separate buckets for each client to avoid hot partitions.


Initial key name 0: `client_id/file_hash-YYYY-MM-DD-HH/epoch_timestamp.png`

Better key name 1: `file_hash/client_id/batchid/YYYY-MM-DD/epoch_timestamp-debug.png`

e.g. `cat-wrangler-dest-ice666-dev/0eaf1da24040970c6396ca59488ad7fa739ef7ab4ee1f757f180dade9adc43cf/stablecaps900/batch-1744481929/2025-04-12-18/1744481929-debug.png`

*Note: The `-debug` part of the key is added by the client so that the lambda can store logs for power users.*

#### Why key name 1 is a good choice for better partition distribution, scalability, and performance for high-volume workloads:

1. Randomness: file_hash provides randomness for partition distribution.
2. client_id is included in the key, allowing logical grouping of objects by client. S3 items are stored flat, and hierarchical folder structures are an illusion. i.e. the entire key can be search with something like `key.contains(client_id)`
3. No Redundancy: reduces the key length without losing functionality.
4. Chronological Organization: `YYYY-MM-DD` and `epoch_timestamp` are retained for human-readable organization and uniqueness.

## Solutions to Balance Performance and Searchability:
The S3 key name is designed for performance at the expense of searchability. In order to balance this we have the following options:

### 1. Use a Metadata-Based Search
Instead of relying solely on the S3 key structure, store metadata about each object in a database (e.g., DynamoDB). For example: - Store the `client_id`, `file_hash`, and S3 key (`s3img_key`) in a DynamoDB table. Then, query DynamoDB to find all objects for a specific `client_id`, and use the S3 key (`s3img_key`) to retrieve the objects from S3.

**Advantages:** S3 key structure can remain optimized for performance (e.g., with random prefixes).We can efficiently search for objects by client_id using DynamoDB.

**Disadvantages:** Requires maintaining a separate database (DynamoDB) and keeping it in sync with S3.

### 2. Use a Hybrid Key Structure
We can include the `client_id` as part of the random prefix to retain some logical grouping while still improving performance. For example: `file_hash/client_id/YYYY-MM-DD/epoch_timestamp.png`.

**Advantages:** Improves partition distribution while still allowing some level of searchability by `client_id`.

**Disadvantages:** Slightly more complex key structure. - Searching by `client_id` still requires additional processing to filter results.

### 3. Use S3 Inventory or Tags
* Use S3 Inventory to generate a report of all objects in the bucket, including their metadata (e.g., `client_id` stored as part of the key or as an object tag).

* Alternatively, use S3 Object Tags to tag each object with its `client_id` and other metadata. We can then use the GetObjectTagging API to search for objects by tag.

**Advantages:** Allows searching by `client_id` without relying on the key structure. - Tags are stored directly in S3, so no additional database is required.

**Disadvantages:**  S3 Inventory reports are not real-time (they are generated periodically). Searching by tags can be slower compared to querying a database.
