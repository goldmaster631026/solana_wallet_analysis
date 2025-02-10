
# import requests
# import json
# from solders.pubkey import Pubkey

# def get_account_info(account_address):
#     """
#     Retrieves account information from the Solana Devnet.

#     Args:
#         account_address (str): The public key of the account to query.

#     Returns:
#         dict: The account information as a dictionary, or None if an error occurs.
#     """
#     url = "https://api.mainnet-beta.solana.com"
#     headers = {"Content-Type": "application/json"}
#     data = {
#         "jsonrpc": "2.0",
#         "id": 1,
#         "method": "getAccountInfo",
#         "params": [
#             account_address,
#             {
#                 "encoding": "jsonParsed",  # Use jsonParsed for easier data access
#                 "commitment": "processed" #commitment level
#             }
#         ]
#     }

#     try:
#         response = requests.post(url, headers=headers, data=json.dumps(data))
#         response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
#         result = response.json()

#         if result.get("error"):
#             print(f"Error from Solana API: {result['error']}")
#             return None

#         return result.get("result")  # Return the result part of the json
#     except requests.exceptions.RequestException as e:
#         print(f"Request failed: {e}")
#         return None
#     except json.JSONDecodeError as e:
#         print(f"Failed to decode JSON response: {e}")
#         return None


# def get_owner_address(account_address):
#     """
#     Retrieves the owner address of a Solana account.

#     Args:
#         account_address (str): The public key of the account.

#     Returns:
#         str: The owner address as a string, or None if not found or an error occurs.
#     """
#     account_info = get_account_info(account_address)

#     if account_info and account_info.get("value"):
#         return account_info["value"]["owner"]
#     else:
#         print(f"Could not retrieve account info for address {account_address} or account doesn't exist.")
#         return None


# def main():
#     """
#     Main function to demonstrate retrieving and printing the owner address of a Solana account.
#     """
#     # Replace with the Solana account address you want to query
#     account_address_raydium = [
#         "DhHVd5s4hqBGnTkFztsK98WGPtYUJjpUCqNnWaNLWb4F",
#         "2hZyFZEtpUYYXuyhNPTsKCPTRNyVyFrMWhAqWnPXUEda",
#         "48ZvQCvJ8n2AtXSXSBkndkKBADuf6NSWSa5Zuf6C8xUi",
#         "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",
#         "4d4mfoHAruJkMJDNzSJ9eyXphnDdsDSNEZFVApqhu8xL",
        
#     ]
#     for account in account_address_raydium :
#         owner_address = get_owner_address(account)

#         if owner_address:
#             print(f"The owner address of account {account} is: {owner_address}")
#         else:
#             print(f"Failed to retrieve the owner address for account {account_address}.")

# if __name__ == "__main__":
#     main()



# Replace 'YOUR_API_KEY' with your actual Helius API key
api_key = "97f3ea30-7f8b-4c10-a368-1160df74ed5b"
asset_id = "J5vBmSwngfd9m8rxYACYtFJYKJNW1xhy6xJmp3nMxbfG"

from solders.pubkey import Pubkey
from solana.rpc.api import Client
import json
import base64
# from utils import LIQUIDITY_STATE_LAYOUT_V4


def get_token_amounts_example():
    endpoint = 'https://api.mainnet-beta.solana.com'
    solana_client = Client(endpoint)
    pool_address = 'J5vBmSwngfd9m8rxYACYtFJYKJNW1xhy6xJmp3nMxbfG' # SOL-USDC
    pool = Pubkey.from_string(pool_address)
    info = json.loads(solana_client.get_account_info_json_parsed(pool).to_json())
    data = info['result']['value']['data']
    data_64 = base64.b64decode(data[0])
    print(data)
    # token_account_data = LIQUIDITY_STATE_LAYOUT_V4.parse(data_64)

    # marketId = Pubkey.from_bytes(token_account_data.marketId)
    # base_token_account = Pubkey.from_bytes(token_account_data.baseVault)
    # quote_token_account = Pubkey.from_bytes(token_account_data.quoteVault)
    # owner = Pubkey.from_bytes(token_account_data.owner)


    # print('marketId', marketId)
    # print('base_token_account', base_token_account)
    # print('quote_token_account', quote_token_account)
    # print('owner', owner)

    # base_token_info = solana_client.get_token_account_balance(base_token_account).to_json()
    # base_token_info = json.loads(base_token_info)
    # quote_token_info = solana_client.get_token_account_balance(quote_token_account).to_json()
    # quote_token_info = json.loads(quote_token_info)
    # owner_token_info = solana_client.get_token_account_balance(owner).to_json()
    # owner_token_info = json.loads(owner_token_info)

    # print('base_token_info', base_token_info)
    # print('quote_token_info', quote_token_info)
    # print('owner_token_info', owner_token_info)

get_token_amounts_example()
