# Dealer Platform SAM v2 - quick start

This stack intentionally uses `samv2` names so it can coexist with the current console-created `dealer-platform-*` resources.

## Cost warning
`AWS::WAFv2::WebACL` is billable while provisioned. Delete the stack after the demo if you do not want ongoing WAF charges.

## Deploy
```bash
cd dealer-platform-samv2
sam validate --lint
sam build
sam deploy --guided
```

For the first guided deployment:
- Stack name: `dealer-platform-samv2-dev`
- Region: `eu-central-1`
- Allow IAM role creation: yes
- FailureEmail: leave blank, or enter your email if you want an SNS subscription

## Seed one product after deployment
Get the table name from stack Outputs, then add:
- product_id: `CAR-001`
- name: `Model A`
- price: `42000`
- inventory: `10`

## Cognito
The stack creates a separate user pool and app client. Create a test user and verify:
- missing/invalid Authorization token -> blocked by the API authorizer
- valid Cognito token -> API reaches Lambda

## WAF proof
The Web ACL contains a harmless demo rule that blocks requests whose `User-Agent` contains:
`BlockedDemoClient`

A normal request should pass WAF (then Cognito applies).
A request with that user agent should receive a WAF block response.

## Acceptance path
1. Seed `CAR-001`
2. Obtain a Cognito token
3. GET `/products`
4. POST `/orders` with an `Idempotency-Key`
5. Verify Step Functions -> DynamoDB -> EventBridge -> SQS -> Fulfillment
6. Run one controlled CreateOrder failure if you want to re-prove Saga compensation

## Cleanup
Once evidence/screenshots are captured:
```bash
sam delete --stack-name dealer-platform-samv2-dev --region eu-central-1
```

Note: deleting the stack removes the WAF and other stack-owned resources. Keep the GitHub repository and screenshots.
