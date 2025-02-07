import requests
import json

response = requests.post(
    "https://mainnet.helius-rpc.com/?api-key=97f3ea30-7f8b-4c10-a368-1160df74ed5b",
    headers={"Content-Type":"application/json"},
    json={"jsonrpc":"2.0","id":"test","method":"getAssetBatch","params":{"ids":["Gx2Uf4fmxuo1hjoRnCiNh8vLKPSY2zYYv52MXFU7R6TZ"]}}
)
data = response.json()
parsed_data = json.loads(json.dumps(data))
token_name = parsed_data['result'][0]['content']['metadata']['name']
print(token_name)
print(data)
# print(type(data))