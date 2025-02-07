import requests, json
response = requests.post(
    "https://mainnet.helius-rpc.com/?api-key=97f3ea30-7f8b-4c10-a368-1160df74ed5b",
    headers={"Content-Type":"application/json"},
    json={"jsonrpc":"2.0","id":"test","method":"getAssetBatch","params":{"ids":["8r8VYJVLj3dCg2geHW7Ajkhq3st7LHcTpy7uB9Q5z8a6"]}}
)
data = response.json()
parsed_data = json.loads(json.dumps(data))
token_name = parsed_data['result'][0]['content']['metadata']['name']
token_symbol = parsed_data['result'][0]['content']['metadata']['symbol']
print(token_name)