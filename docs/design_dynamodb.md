# DynamoDB Table design

## Use cases
* Assume the user has a whole bunch of images they wish to categorise and they upload a single or multiple images to s3 bucket. We need to track image hash to avoid reprocessing and to cerate s3 file name. we also need to store logs in case debug flag is provided.


1. batch_id: user would either want to retrieve the results for a small - medium submission. i.e. 1-20 images.
2. batch_id: find by suceed, fail, pass.
3. client_id: find by suceed, fail, pass.
4. batch_id: track logs associated with a batch submission or a single submission.
5. img_fprint: user would want to get the results associated with a specific image submission.
6. img_fprint multiple: user would want to get the results associated with multiple image submissions.
7. batch_id: Find all results sharing a given batch_id collected during a time range.
8. client_id: Find all results sharing a given batch_id collected during a time range.

~~9. Handle cases where the user does not know the hash or S3 filename.~~


# DynamoDB Table Design

## **Table Name**: IceCatWrangler

### **Primary Key**
- **Partition Key (PK)**: `batch_id` (number) - Groups images in a batch.
- **Sort Key (SK)**: `img_fprint` (string) - Unique image hash for each image.

---

### **Attributes**

| **Name**         | **Type**   | **Description**                                                                 |
|-------------------|------------|---------------------------------------------------------------------------------|
| `img_fprint`      | String     | Unique image hash (used as the sort key).                                       |
| `batch_id`        | Number     | Batch ID for grouping images (used as the partition key).                      |
| `client_id`       | String     | Unique ID for the client.                                                      |
| `s3img_key`       | String     | S3 bucket key (source/destination/failure).                                    |
| `file_name`       | String     | Original file name.                                                            |
| `op_status`       | String     | Processing status (e.g., pending, success, fail).                              |
| `rek_resp`        | JSON       | Rekognition response.                                                          |
| `rek_iscat`       | Boolean    | Indicates whether the image contains a cat.                                    |
| `logs`            | JSON       | Debug logs for troubleshooting.                                                |
| `current_date`       | Number     | Upload timestamp (epoch).                                                      |
| `upload_ts`       | Number     | Upload timestamp (epoch).                                                      |
| `rek_ts`          | Number     | Rekognition processing timestamp (epoch).                                      |
| `ttl`             | Number     | Time-to-live in seconds (used for automatic deletion of items after expiration).|

---

### **Global Secondary Indexes (GSIs)**

| **Index Name** | **Partition Key** | **Sort Key**    | ### Use Case**                                                                 |
|-----------------|-------------------|-----------------|-----------------------------------------------------------------------------|
| **GSI1**        | `batch_id`        | `upload_ts`     | Retrieve all objects for a given `batch_id` in a time range.                |
| **GSI2**        | `client_id`       | `upload_ts`     | Retrieve all images uploaded by a client in a time range.                   |
| **GSI3**        | `batch_id`        | `client_id`     | Retrieve images by `batch_id` and `client_id`.                              |
| **GSI4**        | `batch_id`        | `op_status`     | Retrieve images by `batch_id` and processing status (success, fail, pass).  |
| **GSI5**        | `rek_iscat`       | `upload_ts`     | Retrieve images that contain a cat (`rek_iscat = true`).                    |

~~| **GSI6**        | `file_name`       | `upload_ts`     | Retrieve images when the user does not know the hash or S3 filename.        |~~

---

### **Sparse Indexes**

| **Index Name** | **Partition Key** | **Sort Key**    | ### Use Case**                                                                 |
|-----------------|-------------------|-----------------|-----------------------------------------------------------------------------|
| **SparseLogs**  | `batch_id`        | `logs`          | Retrieve debug logs for a specific batch (only indexed when `logs` exist).  |

---

### **Notes**
- **Composite Primary Key**: The primary key (`batch_id` + `img_fprint`) improves batch-level queries and avoids the need for a GSI for batch retrieval.
- **GSIs**: GSIs (`GSI4`, `GSI5`, `GSI6`) support querying by `op_status`, `rek_iscat`, and `client_id` within a batch.
- **Sparse Index**: The `SparseLogs` index is only created for items with `logs`, reducing storage costs and improving query efficiency for debug-related use cases.
- **TTL**: The `ttl` attribute ensures automatic deletion of expired items after a specified time (in seconds), reducing storage costs.
- **High Cardinality**: Partition keys (`batch_id`, `client_id`) are designed to have high cardinality to avoid hot partitions and ensure even traffic distribution.


## Use case example queries (to be tested)

### Use Case 1: Retrieve results for a small-medium submission (1-20 images) by batch_id.

```
response = table.query(
    KeyConditionExpression="batch_id = :batch_id",
    ExpressionAttributeValues={
        ":batch_id": 12345
    },
    Limit=20
)
print(response['Items'])
```

**Performance:**

**RCUs:** 1 RCU for every 4 KB of data read. For 20 items of 1 KB each, 5 RCUs are consumed.

**Latency:** Sub-millisecond to single-digit milliseconds.

### Use Case 2: Find results by batch_id and op_status (e.g., success, fail, pass).

```
response = table.query(
    IndexName="GSI4",
    KeyConditionExpression="batch_id = :batch_id AND op_status = :status",
    ExpressionAttributeValues={
        ":batch_id": 12345,
        ":status": "success"
    }
)
print(response['Items'])
```

**Performance**

**RCUs:** Efficient due to the indexed op_status. For 10 items of 1 KB each, 3 RCUs are consumed.

**Latency:** Sub-millisecond to single-digit milliseconds.

### Use Case 3: Retrieve logs for a specific batch_id.

```
response = table.query(
    KeyConditionExpression="batch_id = :batch_id",
    ExpressionAttributeValues={
        ":batch_id": 12345
    },
    ProjectionExpression="logs"
)
print(response['Items'])
```
**Performance**

**RCUs:** ProjectionExpression reduces the amount of data read. For 10 items with 1 KB logs, 3 RCUs are consumed.

**Latency:** Sub-millisecond to single-digit milliseconds.

### Use Case 4: Retrieve results for a specific image by img_fprint.

```
response = table.query(
    KeyConditionExpression="batch_id = :batch_id AND img_fprint = :img_fprint",
    ExpressionAttributeValues={
        ":batch_id": 12345,
        ":img_fprint": "unique_image_hash"
    }
)
print(response['Items'])
```

**Performance**

**RCUs:** Single-item retrieval consumes 0.5 RCUs for items up to 4 KB.

**Latency:** Sub-millise

### Use Case 5: Retrieve results for multiple images by img_fprint.

```
response = table.batch_get_item(
    RequestItems={
        'IceCatWrangler': {
            'Keys': [
                {'batch_id': 12345, 'img_fprint': 'hash1'},
                {'batch_id': 12345, 'img_fprint': 'hash2'}
            ]
        }
    }
)
print(response['Responses']['IceCatWrangler'])
```

**Performance**

**RCUs:** BatchGet retrieves up to 100 items or 16 MB of data in a single request. For 10 items of 1 KB each, 3 RCUs are consumed.

**Latency:** Single-digit milliseconds for up to 100 items.

### Use Case 6: Retrieve all results for a batch_id in a time range.

```
response = table.query(
    IndexName="GSI1",
    KeyConditionExpression="batch_id = :batch_id AND upload_ts BETWEEN :start AND :end",
    ExpressionAttributeValues={
        ":batch_id": 12345,
        ":start": 1672531200,
        ":end": 1672617600
    }
)
print(response['Items'])
```

**Performance**

**RCUs:** Efficient for time-range queries due to the indexed upload_ts. For 10 items of 1 KB each, 3 RCUs are consumed.

**Latency:** Sub-millisecond to single-digit milliseconds.



### Use Case 7: Retrieve images uploaded by a specific client_id in a time range.

```
response = table.query(
    IndexName="GSI2",
    KeyConditionExpression="client_id = :client_id AND upload_ts BETWEEN :start AND :end",
    ExpressionAttributeValues={
        ":client_id": "client123",
        ":start": 1672531200,
        ":end": 1672617600
    }
)
print(response['Items'])
```

**Performance**

**RCUs:** Efficient for time-range queries. For 10 items of 1 KB each, 3 RCUs are consumed.

**Latency:** Sub-millisecond to single-digit milliseconds.


**Performance**

**RCUs:** Depends on the number of items matching the file_name. For 10 items of 1 KB each, 3 RCUs are consumed.
**Latency:** Sub-millisecond to single-digit milliseconds.

### General Notes on Performance
1. RCU/WCU Optimization:
    * Use ProjectionExpression to retrieve only necessary attributes, reducing RCUs.
    * Use batch_get_item for bulk retrievals to minimize latency and costs.

2. Index Design:
    * GSIs are optimized for specific queries (e.g., time-based retrievals using upload_ts as the sort key).
    * Sparse indexes (e.g., SparseLogs) reduce storage costs and improve query efficiency.
    * Note GSIs increase cost. So edge case GSIs can be eliminated if use cases are rarely used.

3. **Latency:**
    * DynamoDB queries are typically sub-millisecond to single-digit milliseconds, depending on the size of the dataset and the complexity of the query.
