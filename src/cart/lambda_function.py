import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

table = boto3.resource("dynamodb").Table(os.environ["CART_TABLE"])

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
    method = event.get("httpMethod")
    user_id = (event.get("pathParameters") or {}).get("user_id")
    if not user_id:
        return response(400, {"message": "user_id is required"})

    if method == "GET":
        result = table.query(KeyConditionExpression=Key("user_id").eq(user_id))
        return response(200, {"user_id": user_id, "items": result.get("Items", [])})

    if method == "PUT":
        body = json.loads(event.get("body") or "{}")
        product_id = body.get("product_id")
        quantity = body.get("quantity")
        if not product_id or quantity is None:
            return response(400, {"message": "product_id and quantity are required"})

        table.update_item(
            Key={"user_id": user_id, "product_id": product_id},
            UpdateExpression="SET quantity = :q",
            ExpressionAttributeValues={":q": int(quantity)}
        )
        return response(200, {
            "message": "Cart updated",
            "user_id": user_id,
            "product_id": product_id,
            "quantity": int(quantity)
        })

    if method == "DELETE":
        result = table.query(KeyConditionExpression=Key("user_id").eq(user_id))
        with table.batch_writer() as batch:
            for item in result.get("Items", []):
                batch.delete_item(
                    Key={"user_id": user_id, "product_id": item["product_id"]}
                )
        return response(200, {"message": "Cart cleared", "user_id": user_id})

    return response(405, {"message": "Method not allowed"})
