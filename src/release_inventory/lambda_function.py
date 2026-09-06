import json
import os
import boto3

table = boto3.resource("dynamodb").Table(os.environ["PRODUCTS_TABLE"])

def lambda_handler(event, context):
    print(json.dumps({
        "service": "release-inventory",
        "order_id": event.get("order_id"),
        "message": "Compensation started"
    }))

    for item in event.get("items", []):
        table.update_item(
            Key={"product_id": item["product_id"]},
            UpdateExpression="ADD inventory :quantity",
            ExpressionAttributeValues={":quantity": int(item["quantity"])}
        )

    print(json.dumps({
        "service": "release-inventory",
        "order_id": event.get("order_id"),
        "message": "Inventory released"
    }))

    return {
        **event,
        "inventory_released": True,
        "status": "FAILED_COMPENSATED"
    }
