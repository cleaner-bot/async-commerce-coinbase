
# async-commerce-coinbase

async api for coinbase ecommeree

this is still a WIP

## usage

API usage

```py
from async_commerce_coinbase import Coinbase


async def main():
    coinbase = Coinbase("your-api-key")
    print(await coinbase.list_invoices().all())
    async for charge in coinbase.list_charges():
        print(charge)


asyncio.run(main())
```

webhook verification (fastapi)
```py
from async_commerce_coinbase import webhook, exceptions

@app.post("/webhook")
async def coinbase_webhook(request: Request):
    signature = request.headers.get("X-CC-Webhook-Signature", None)
    if signature is None:
        raise HTTPException(400, "Missing signature")
    
    payload = await request.body()
    try:
        event = webhook.verify_signature(payload, "webhook-secret", signature)
    except exceptions.CoinbaseSignatureVerificationError:
        raise HTTPException(400, "Invalid signature")
    
    print(event)  # process event
```
