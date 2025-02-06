import requests

response = requests.post(
    "https://mainnet.helius-rpc.com/?api-key=97f3ea30-7f8b-4c10-a368-1160df74ed5b",
    headers={"Content-Type":"application/json"},
    json={"jsonrpc":"2.0","id":1,"method":"getTransaction","params":["2nBhEBYYvfaAe16UMNqRHre4YNSskvuYgx3M6E4JP1oDYvZEJHvoPzyUidNgNX5r9sTyN1J9UxtbCXy2rqYcuyuv","json"]}
)
data = response.json()
print(data)