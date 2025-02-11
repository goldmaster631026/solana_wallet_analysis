# from solders.pubkey import Pubkey

# PUMP_PROGRAM_ID = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
# PUMP_CURVE_SEED = b"bonding-curve"

# def find_pump_curve_address(token_mint: Pubkey) -> Pubkey:
#     """
#     Calculates the Pump.fun bonding curve address for a given token mint.
#     """
#     curve_address, _ = Pubkey.find_program_address(
#         [PUMP_CURVE_SEED, bytes(token_mint)],
#         PUMP_PROGRAM_ID,
#     )
#     return curve_address

# # Token mint address
# token_mint_address = Pubkey.from_string("EMNtsQExBsMB6znWCCgr4PpgD5yyvy3XumAKvcHnpump")
# curve_address = find_pump_curve_address(token_mint_address)
# print(f"The bonding curve address is: {curve_address}")

import requests
import json

def get_sol_balance_change(signature, helius_api_key):
    """
    Retrieves the SOL balance change for a given transaction signature using the Helius RPC.

    Args:
        signature (str): The transaction signature to query.
        helius_api_key (str): Your Helius API key.

    Returns:
        float: The SOL balance change as a float, or None if an error occurred.
    """
    url = f"https://mainnet.helius-rpc.com/?api-key=97f3ea30-7f8b-4c10-a368-1160df74ed5b"
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getConfirmedTransaction",
        "params": [
            signature,
            "jsonParsed",
        ],
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        result = response.json()

        # Extract SOL balance changes
        account_keys = result['result']['transaction']['message']['accountKeys']
        pre_balances = result['result']['meta']['preBalances']
        post_balances = result['result']['meta']['postBalances']

        # Identify SOL accounts and calculate balance changes
        sol_balance_changes = {}
        for i, account_key in enumerate(account_keys):
            if account_key:  # Check if the account key is not empty
                pre_balance = pre_balances[i]
                post_balance = post_balances[i]
                balance_change = (post_balance - pre_balance) / 1000000000  # Convert lamports to SOL
                sol_balance_changes[account_key] = balance_change

        return sol_balance_changes

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except (KeyError, TypeError) as e:
        print(f"Error parsing response: {e}")
        return None

# Example usage (replace with your actual signature and API key)
signature = "W68L4GzQLapfDynmu86bDoDrrSFKQt3LsvUY1DMYTJjgoCdkwNELcLaK7SanXcxuHV8tzB4LpdRLPPGuwEaAL6h"
helius_api_key = "97f3ea30-7f8b-4c10-a368-1160df74ed5b"

sol_balance_changes = get_sol_balance_change(signature, helius_api_key)

if sol_balance_changes:
    print("SOL Balance Changes:")
    for account, change in sol_balance_changes.items():
        print(f"Account: {account}, Change: {change:.4f} SOL")
else:
    print("Failed to retrieve SOL balance changes.")

