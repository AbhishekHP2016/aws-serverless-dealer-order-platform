import json

def lambda_handler(event, context):
    user_id = event.get("user_id")
    items = event.get("items")

    valid = bool(user_id and isinstance(items, list) and len(items) > 0)
    if valid:
        for item in items:
            if not item.get("product_id") or int(item.get("quantity", 0)) <= 0:
                valid = False
                break

    result = {**event, "valid": valid}
    if not valid:
        result["reason"] = "Invalid user_id/items/order quantities"

    print(json.dumps({
        "service": "validate-order",
        "order_id": event.get("order_id"),
        "valid": valid
    }))
    return result
