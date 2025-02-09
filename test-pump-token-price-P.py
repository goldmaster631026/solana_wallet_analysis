from solders.pubkey import Pubkey
from base64 import b64decode
import requests
import struct  # Import the struct module

# Your Helius API key
HELIUS_API_KEY = "97f3ea30-7f8b-4c10-a368-1160df74ed5b"  # Replace with your actual Helius API key

# Pump.fun Bonding Curve Program ID (Replace with the actual program ID)
PUMP_BONDING_CURVE_PROGRAM_ID = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")  #Example, replace it.

# Function to get account info from Helius RPC
def get_account_info(account_pubkey: Pubkey):
    url = f"https://rpc.helius.xyz/?api-key={HELIUS_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [
            str(account_pubkey),
            {
                "encoding": "base64",
                "commitment": "confirmed",
                "dataSlice": {
                    "offset": 0,
                    "length": 5000,  # Adjust length as needed
                },
            },
        ],
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get("result")
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Account Data Structure (YOU MUST FILL THIS IN BASED ON THE PROGRAM'S DATA LAYOUT)
# This is an EXAMPLE - REPLACE WITH THE ACTUAL STRUCTURE
def decode_bonding_curve_data(data):
    """
    Decodes the base64 encoded bonding curve data.  This is a placeholder.
    YOU MUST DETERMINE THE CORRECT DATA LAYOUT.

    Args:
        data: The base64 encoded data string.

    Returns:
        A dictionary containing the decoded fields, or None if an error occurs.
    """
    decoded_data = b64decode(data)

    # Example: Assuming the first 8 bytes are virtual SOL reserves (u64), and the next 8 bytes are token reserves (u64)
    if len(decoded_data) < 16:
        print("Error: Not enough data in the account.")
        return None

    try:
        virtual_sol_reserves = struct.unpack("<q", decoded_data[16:24])[0]  # '<q' is little-endian signed long long (8 bytes)
        token_reserves = struct.unpack("<q", decoded_data[8:16])[0]  # '<q' is little-endian signed long long (8 bytes)


        return {
            "virtual_sol_reserves": virtual_sol_reserves,
            "token_reserves": token_reserves,
        }
    except struct.error as e:
        print(f"Error decoding data: {e}")
        return None

# List of account keys to check
accountKeys =  [
          {
            'pubkey': 'EMKrEDuahN9iWafms47x5fPqZYTh5XtpSsjRz3gLi3Pg',
            'signer': True,
            'source': 'transaction',
            'writable': True
          },
          {
            'pubkey': 'CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM',
            'signer': False,
            'source': 'transaction',
            'writable': True
          },
          {
            'pubkey': 'CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM',
            'signer': False,
            'source': 'transaction',
            'writable': True
          },
          {
            'pubkey': '63ooTk2JDjbqnuBjrCFx5BDUqv5eitvNUWJ8UpZXeuWi',
            'signer': False,
            'source': 'transaction',
            'writable': True
          }
]

# Iterate through the account keys
for account_key in accountKeys:
    pubkey_string = account_key['pubkey']
    pubkey = Pubkey.from_string(pubkey_string)

    account_info = get_account_info(pubkey)

    if account_info:
        owner_program_id = account_info.get("value").get("owner")
        owner_program_id_pubkey = Pubkey.from_string(owner_program_id)

        if owner_program_id_pubkey == PUMP_BONDING_CURVE_PROGRAM_ID:
            print(f"Pubkey {pubkey_string} is a bonding curve address. Processing...")

            # Get Account Data
            account_data = account_info.get("value").get("data")[0]

            # Decode the account data using the defined structure
            decoded_data = decode_bonding_curve_data(account_data)

            if decoded_data:
                virtual_sol_reserves = decoded_data["virtual_sol_reserves"] / 1000000000
                token_reserves = decoded_data["token_reserves"] / 1000000

                # Calculate the price
                if token_reserves != 0:  # Prevent division by zero
                    price = virtual_sol_reserves / token_reserves
                    print(f"Price: {price}")

                    # Calculate the market cap (total supply is 1 billion)
                    total_supply = 1_000_000_000
                    market_cap = price * total_supply
                    # print(f"Market Cap: {market_cap}")
                else:
                    print("Token reserves are zero. Cannot calculate price.")
            else:
                print("Failed to decode account data.")
        else:
            print(f"Pubkey {pubkey_string} is NOT a bonding curve address. Owner: {owner_program_id}")
    else:
        print(f"Failed to retrieve account info for {pubkey_string}.")
