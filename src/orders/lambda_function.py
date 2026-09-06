import json
import os
import uuid
import boto3
from decimal import Decimal

sfn = boto3.client("stepfunctions")
orders_table = boto3.resource("dynamodb").Table(os.environ["ORDERS_TABLE"])
STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]

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

    if method == "POST":
        headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
        idempotency_key = headers.get("idempotency-key")
        if not idempotency_key:
            return response(400, {"message": "Idempotency-Key is required"})

        body = json.loads(event.get("body") or "{}")
        user_id = body.get("user_id")
        items = body.get("items")
        if not user_id or not items:
            return response(400, {"message": "user_id and items are required"})

        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        workflow_input = {
            "order_id": order_id,
            "user_id": user_id,
            "idempotency_key": idempotency_key,
            "items": items
        }
        execution = sfn.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps(workflow_input)
        )
        return response(202, {
            "message": "Order processing started",
            "order_id": order_id,
            "executionArn": execution["executionArn"]
        })

    if method == "GET":
        order_id = (event.get("pathParameters") or {}).get("order_id")
        if not order_id:
            return response(400, {"message": "order_id is required"})
        result = orders_table.get_item(Key={"order_id": order_id})
        order = result.get("Item")
        if not order:
            return response(404, {"message": "Order not found", "order_id": order_id})
        return response(200, order)

    return response(405, {"message": "Method not allowed"})
