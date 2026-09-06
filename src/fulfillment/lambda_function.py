import json

def lambda_handler(event, context):
    for record in event.get("Records", []):
        envelope = json.loads(record["body"])
        detail = envelope.get("detail", {})
        print(json.dumps({
            "service": "fulfillment-order",
            "order_id": detail.get("order_id"),
            "user_id": detail.get("user_id"),
            "status": detail.get("status"),
            "message": "Order received for fulfillment"
        }))

    return {"processed": True}
