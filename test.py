from moralis import sol_api

api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6ImY1NjlhZTRlLTdlNjAtNDRhYS04MDMxLWJmNDllZDcxMTU2NCIsIm9yZ0lkIjoiNDI5OTk1IiwidXNlcklkIjoiNDQyMzA2IiwidHlwZUlkIjoiNWM1MmZjMGMtMTgwMS00ZWRjLWI1NDAtN2ViNjk1MzBkMmFhIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3Mzg5Mjc0MTQsImV4cCI6NDg5NDY4NzQxNH0.xqc7QBe_NBQ5od0_NRlw3Z6xicCuv2DqRVtkVqS_r8o"
params = {
    "address": "9ak8pEr1HZxcBB2pZGPBFTuhw4VB8zUPLqmFiZKzpup",
    "network": "mainnet",
}

result = sol_api.token.get_token_price(
    api_key=api_key,
    params=params,
)

print(float(result.get('nativePrice', {}).get('value')) / 1000000000)
# print(result)
