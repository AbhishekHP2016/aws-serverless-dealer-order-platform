import json
import os
import boto3
from decimal import Decimal

table = boto3.resource("dynamodb").Table(os.environ["PRODUCTS_TABLE"])

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError

def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body, default=decimal_default)
    }

def lambda_handler(event, context):
    product_id = (event.get("pathParameters") or {}).get("product_id")
    if product_id:
        result = table.get_item(Key={"product_id": product_id})
        item = result.get("Item")
        if not item:
            return response(404, {"message": "Product not found", "product_id": product_id})
        return response(200, item)

    result = table.scan()
    return response(200, {"products": result.get("Items", [])})
