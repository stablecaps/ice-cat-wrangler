import json


def get_result(event, context):
    body = {
        "message": "Go Serverless v4.0! Your function executed successfully!"
    }

    return {"statusCode": 200, "body": json.dumps(body)}
