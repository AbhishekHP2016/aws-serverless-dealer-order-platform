import json
import os
import boto3
from botocore.exceptions import ClientError

table = boto3.resource("dynamodb").Table(os.environ["PRODUCTS_TABLE"])

def lambda_handler(event, context):
    print(json.dumps({
        "service": "reserve-inventory",
        "order_id": event.get("order_id"),
        "message": "Inventory reservation started"
    }))

    for item in event.get("items", []):
        product_id = item["product_id"]
        quantity = int(item["quantity"])
        try:
            table.update_item(
                Key={"product_id": product_id},
                UpdateExpression="SET inventory = inventory - :quantity",
                ConditionExpression="attribute_exists(product_id) AND inventory >= :quantity",
                ExpressionAttributeValues={":quantity": quantity}
            )
        except ClientError as error:
            if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise Exception(f"InsufficientInventory:{product_id}")
            raise

    return {**event, "inventory_reserved": True}
