import json
import os
import boto3
from datetime import datetime, timezone
from botocore.exceptions import ClientError

table = boto3.resource("dynamodb").Table(os.environ["ORDERS_TABLE"])

def lambda_handler(event, context):
    order_id = event["order_id"]
    order = {
        "order_id": order_id,
        "user_id": event["user_id"],
        "items": event["items"],
        "status": "CONFIRMED",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    try:
        table.put_item(
            Item=order,
            ConditionExpression="attribute_not_exists(order_id)"
        )
    except ClientError as error:
        if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise Exception(f"OrderAlreadyExists:{order_id}")
        raise

    print(json.dumps({
        "service": "create-order",
        "order_id": order_id,
        "status": "CONFIRMED"
    }))

    return {**event, "status": "CONFIRMED", "order_created": True}
