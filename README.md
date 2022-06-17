
# async-commerce-coinbase

Simple, fully typed and mypy compliant async api for coinbase commerce.

There are no plans to convert the returned json dictionaries by coinbase into
python objects to support new or deleted fields without erroring.

This project is still under heavy development and version pinning is highly recommended.

## Installation

This project is still under development and not yet available on pypi, but you
can install directly from Github:

```
async_commerce_coinbase@git+https://github.com/cleaner-bot/async-commerce-coinbase.git
```

To pin a certain version at `@version` to the end of the URL. (eg `@v0.1.0`)

## Usage

First you need to import and instantiate a coinbase client:

```py
from async_commerce_coinbase import Coinbase


async def main():
    coinbase = Coinbase("your-api-key")
    print(coinbase)


asyncio.run(main())
```

See [full api](#full-api) for a list of all API calls available.

## Pagination

```py
async def main():
    coinbase = Coinbase("your-api-key")
    # .all() returns a list of all invoices
    print(await coinbase.list_invoices().all())
    # a paginator can also be used in an async for loop
    async for charge in coinbase.list_charges():
        print(charge)
    # or if you want it chunked
    async for charges in coinbase.list_charges().chunk(10):
        # charges will be a list with 10 charges if there are more than 10 left
        print(charges)

```


## Webhook verification

You can use the `webhook.verify_signature` API to verify the signature of
the webhook body and get a fully type hinted response.

```py
from async_commerce_coinbase import webhook, CoinbaseSignatureVerificationError

COINBASE_WEBHOOK_IPS = ipaddress.IPv4Network("54.175.255.192/27")


@app.post("/webhook")
async def coinbase_webhook(request: Request):
    # coinbase sends all requests from 54.175.255.192/27
    ip = request.headers.get("cf-connecting-ip", None)
    if ip is None or ipaddress.IPv4Address(ip) not in COINBASE_WEBHOOK_IPS:
        raise HTTPException(400, "IP lookup failed.")

    # coinbase puts the signature into this header
    signature = request.headers.get("X-CC-Webhook-Signature", None)
    if signature is None:
        raise HTTPException(400, "Missing signature")
    
    payload = await request.body()
    # save the secret somewhere secure
    secret = os.getenv("CC_WEBHOOK_SECRET")
    try:
        event = webhook.verify_signature(payload, secret, signature)
    except CoinbaseSignatureVerificationError:
        raise HTTPException(400, "Invalid signature")
    
    print(event)  # process event
```


## Full API

Assume the following runs in an async function.

Note: `.all()` is a very slow function if you have hundreds of items,
consider using `.chunk()` or iterating over it instead.

```py
# using charge api
print(await coinbase.list_charges().all())  # print all existing charges
charge = await coinbase.create_charge(
    name="Test Charge",
    description="This is a test charge for async-commerce-coinbase.",
    pricing_type="fixed_price",  # either fixed_price or no_price
    local_price={"amount": 10, "currency": "EUR"},
    redirect_url="https://example.com/success",
    cancel_url="https://example.com/cancelled",
    metadata={"is_test": True}
)
# redirect user to charge["hosted_at"]
print(charge["hosted_at"])

# ideally this happens in a webhook or something because the charge
# will be outdated or use get_charge() to refresh it
# charge = await coinbase.get_charge(charge["id"])
status = charge["timeline"][-1]["status"]
if status == "UNRESEOLVED":
    await coinbase.resolve_charge(charge["id"])
elif stauts == "NEW":
    await coinbase.cancel_charge(charge["id"])


# using checkout api
print(await coinbase.list_checkouts().all())  # print all existing checkouts
checkout = await coinbase.create_checkout(
    name="Test Checkout",
    description="This is a test checkout for async-commerce-coinbase.",
    requested_info=["email"],
    pricing_type="fixed_price",
    local_price={"amount": 10, "currency": "EUR"},
)
# put checkout id into front end somewhere
print(checkout["id"])
# we want name now too
# arguments we dont specify dont change
await coinbase.update_checkout(
    checkout["id"],
    requested_info=["name", "email"],
)
# no longer want it
await coinbase.delete_checkout(checkout["id"])

# using invoice api
print(await coinbase.list_invoices().all())  # print all existing invoices
invoice = await coinbase.create_invoice(
    business_name="Testing Inc.",
    customer_email="test@example.com",
    local_price={"amount": 10, "currency": "EUR"},
    customer_name="John Doe",
    memo="You are being tested by async-commerce-coinbase!"
)
await coinbase.void_invoice(invoice["id"])
# honestly no idea why you'd use coinbase.resolve_invoice instead of 
# coinbase.resolve_charge with invoice.charge.id

# using event api
print(await coinbase.list_events().all())  # print all existing events
event_id = "..."  # from webhook or list_events ^
evnet = await coinbase.get_event(event_id)
print(event)
```
