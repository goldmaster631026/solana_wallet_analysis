import requests
import pandas as pd
from config import API_KEY , WALLET_ADDRESS
import requests, json, struct
from base64 import b64decode
from moralis import sol_api
from solders.pubkey import Pubkey


HELIUS_API_KEY = "97f3ea30-7f8b-4c10-a368-1160df74ed5b"
PUMP_BONDING_CURVE_PROGRAM_ID = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
# Pump fun token price calculate start ============
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
    
def pump_price_calculate (accountKeys):
    flag_pair_address = 0
    for account_key in accountKeys:
        pubkey_string = account_key['pubkey']
        pubkey = Pubkey.from_string(pubkey_string)

        account_info = get_account_info(pubkey)

        if account_info:
            owner_program_id = account_info.get("value").get("owner")
            
            owner_program_id_pubkey = Pubkey.from_string(owner_program_id)

            if owner_program_id_pubkey == PUMP_BONDING_CURVE_PROGRAM_ID and flag_pair_address == 0:
                
                # print(account_info)
                
                # print(f"Pubkey {pubkey_string} is a bonding curve address. Processing...")
                flag_pair_address = 1
                # Get Account Data
                account_data = account_info.get("value").get("data")[0]

                # Decode the account data using the defined structure
                decoded_data = decode_bonding_curve_data(account_data)

                if decoded_data:
                    virtual_sol_reserves = decoded_data["virtual_sol_reserves"] / 1000000000
                    token_reserves = decoded_data["token_reserves"] / 1000000
                    # print(virtual_sol_reserves)
                    # print(token_reserves)

                    # Calculate the price
                    if token_reserves != 0:  # Prevent division by zero
                        price = virtual_sol_reserves / token_reserves
                        print("\n")
                        print(f"Calculated Price: {price}")
                        return price

                        # Calculate the market cap (total supply is 1 billion)
                        total_supply = 1_000_000_000
                        market_cap = price * total_supply
                        # print(f"Market Cap: {market_cap}")
                    else:
                        return 7070
                        # print("Token reserves are zero. Cannot calculate price.")
                else:
                    continue
                    # print("Failed to decode account data.")
            else:
                continue
                # print(f"Pubkey {pubkey_string} is NOT a bonding curve address.")
        else:
            continue
            # print(f"Failed to retrieve account info for {pubkey_string}.")   
# Pump fun token price calculate end ==============



# Raydium token price calculate start ==========

def get_account_info_raydium(account_address):
    """
    Retrieves account information from the Solana Devnet.

    Args:
        account_address (str): The public key of the account to query.

    Returns:
        dict: The account information as a dictionary, or None if an error occurs.
    """
    url = "https://api.mainnet-beta.solana.com"
    headers = {"Content-Type": "application/json"}
    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [
            account_address,
            {
                "encoding": "jsonParsed",  # Use jsonParsed for easier data access
                "commitment": "processed" #commitment level
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        result = response.json()

        if result.get("error"):
            print(f"Error from Solana API: {result['error']}")
            return None

        return result.get("result")  # Return the result part of the json
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON response: {e}")
        return None
    
def get_owner_address(account_address):
    """
    Retrieves the owner address of a Solana account.

    Args:
        account_address (str): The public key of the account.

    Returns:
        str: The owner address as a string, or None if not found or an error occurs.
    """
    
    account_info = get_account_info_raydium(account_address)

    if account_info and account_info.get("value"):
        # return account_info["value"]
        return account_info["value"]["owner"]
    else:
        # print(f"Could not retrieve account info for address {account_address} or account doesn't exist.")
        return None

def export_owner_address (accountKeys):

    for account in accountKeys :
        account = account['pubkey']
        owner_address = get_owner_address(account)

        if owner_address:
            print(f"The owner address of account {account} is: {owner_address}")
        else:
            continue
            # print(f"Failed to retrieve the owner address for account {account_address}.")

# Raydium token price calculate End ============

def get_Signaturelist(walletaddress) :
    
    response = requests.post(
        "https://mainnet.helius-rpc.com/?api-key=97f3ea30-7f8b-4c10-a368-1160df74ed5b",
        headers={"Content-Type":"application/json"},
        json={"jsonrpc":"2.0","id":"1","method":"getSignaturesForAddress","params":[walletaddress]}
    )
    data = response.json()
    TempSignatureList = []
    if 'result' in data and isinstance(data['result'], list):
        for item in data['result']:
            if 'signature' in item:
 
                TempSignatureList.append(item['signature'])

    return TempSignatureList
def search_substring(my_dict, search_for):
    for key, value in my_dict.items():
        if search_for in str(key) or search_for in str(value):
            return True
    return False

def get_transaction(signature):
    response = requests.post(
        "https://mainnet.helius-rpc.com/?api-key=97f3ea30-7f8b-4c10-a368-1160df74ed5b",
        headers={"Content-Type": "application/json"},
        json={"jsonrpc": "2.0", "id": 1, "method": "getTransaction", "params": [signature, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]}
    )
    data = response.json()
    return data
def get_token_price_from_moralis(token_address):
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6ImY1NjlhZTRlLTdlNjAtNDRhYS04MDMxLWJmNDllZDcxMTU2NCIsIm9yZ0lkIjoiNDI5OTk1IiwidXNlcklkIjoiNDQyMzA2IiwidHlwZUlkIjoiNWM1MmZjMGMtMTgwMS00ZWRjLWI1NDAtN2ViNjk1MzBkMmFhIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3Mzg5Mjc0MTQsImV4cCI6NDg5NDY4NzQxNH0.xqc7QBe_NBQ5od0_NRlw3Z6xicCuv2DqRVtkVqS_r8o"
    params = {
        "address": token_address,
        "network": "mainnet",
    }

    result = sol_api.token.get_token_price(
        api_key=api_key,
        params=params,
    )
    return result.get('nativePrice', {}).get('value')

def update_final_result( new_item, finalresult):
    token_address = new_item[0]['token_address']
    token_name = new_item[0]['token_name']
    token_symbol = new_item[0]['token_symbol']
    buy_amount = new_item[0].get('buy(Token)', 0)
    sell_amount = new_item[0].get('sell(Token)', 0)
    sol_buy = new_item[0].get('sell(Sol)', 0)
    sol_sell = new_item[0].get('buy(Sol)', 0)
    sol_token_price = float(get_token_price_from_moralis(token_address)) / (1000000000)
    print("moralis price " , sol_token_price)
    # sol_token_price_calculated = new_item[0].get('token_price',0)

    for item in finalresult:
        if item['token_address'] == token_address:
            
            item['buy(Token)'] = item.get('buy(Token)', 0) + buy_amount
            item['sell(Token)'] = item.get('sell(Token)', 0) + sell_amount
            item['sol_buy'] = item.get('sol_buy', 0) + sol_buy
            item['sol_sell'] = item.get('sol_sell', 0) + sol_sell
            item['realized_sol'] = item.get('sol_sell') - item.get('sol_buy')
            if item.get('sol_buy') != 0 :
                item['profit_%'] = (item.get('realized_sol')/ item.get('sol_buy')) * 100
            else : item['profit_%'] = 'NA'
            if (item['buy(Token)'] - item['sell(Token)']) > 0 :
                item['unrealized_sol'] = (item['buy(Token)'] - item['sell(Token)']) * sol_token_price
            else : item['unrealized_sol'] = 0
            item['profit_sol'] = item['realized_sol'] + item['unrealized_sol']
           
            return

   
    finalresult.append({
        'token_name' : token_name,
        'token_symbol' : token_symbol,
        'token_address': token_address,
        'buy(Token)': buy_amount,
        'sell(Token)': sell_amount,
        'sol_buy' : sol_buy,
        'sol_sell' : sol_sell,
        'profit_%' : 'NA',
        'realized_sol' : sol_sell - sol_buy,
        'unrealized_sol' : (buy_amount - sell_amount) * sol_token_price if (buy_amount - sell_amount) > 0 else 0,
        'profit_sol' : (sol_sell - sol_buy) + (buy_amount - sell_amount) * sol_token_price if (buy_amount - sell_amount) > 0 else sol_sell - sol_buy
        
        
    })
    
def get_tokens_balances (account_address, transaction_data, signa):
    results = []
        
    pre_token_balances = transaction_data.get('result', {}).get('meta', {}).get('preTokenBalances', [])
    post_token_balances = transaction_data.get('result', {}).get('meta', {}).get('postTokenBalances', [])
    pre_balance = transaction_data.get('result', {}).get('meta', {}).get('preBalances', [])[0]
    post_balance = transaction_data.get('result', {}).get('meta', {}).get('postBalances', [])[0]
    fee_balance = transaction_data.get('result', {}).get('meta', {}).get('fee')
    # print(post_balance)
    # print(pre_balance)
    # print(fee_balance)
    sol_balance = (abs(post_balance - pre_balance) - fee_balance)/ (1000000000)
    # print(sol_balance)
    if post_token_balances :
        for post_balance in post_token_balances:
            if post_balance['owner'] == account_address:
                token_address = post_balance['mint']
                
                
                response = requests.post(
                "https://mainnet.helius-rpc.com/?api-key=97f3ea30-7f8b-4c10-a368-1160df74ed5b",
                headers={"Content-Type":"application/json"},
                json={"jsonrpc":"2.0","id":"test","method":"getAssetBatch","params":{"ids":[token_address]}}
                )
                data = response.json()
                parsed_data = json.loads(json.dumps(data))
                token_name = parsed_data['result'][0]['content']['metadata']['name']
                token_symbol = parsed_data['result'][0]['content']['metadata']['symbol']
                accountKeys = transaction_data.get('result', {}).get('transaction', {}).get('message', {}).get('accountKeys', [])
                print(token_name)
                
                
                where = "Pump" if search_substring(transaction_data, '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P') else "Swap"
                if search_substring(transaction_data, '75kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8') :
                    where = "Raydium"
                if where == "Pump":
                    calculated_pump_token_price = pump_price_calculate(accountKeys)
                    if calculated_pump_token_price == 7070 :
                        continue
                    
                if where == "Raydium" :
                    export_owner_address(accountKeys)
                    
              

                
# sol - 3
# token - 4

                
                post_ui_amount = post_balance['uiTokenAmount']['uiAmount'] if post_balance['uiTokenAmount']['uiAmount'] is not None else 0

                pre_balance = next((pre for pre in pre_token_balances if pre['owner'] == account_address and pre['mint'] == token_address), None)
                # print(pre_balance)
            
                if pre_balance is not None:
                    # pre_ui_amount = pre_balance['uiTokenAmount']['uiAmount'] possible also
                    pre_ui_amount = pre_balance['uiTokenAmount']['uiAmount'] if pre_balance['uiTokenAmount']['uiAmount'] is not None else 0
                    difference = abs(post_ui_amount - pre_ui_amount)
                
                    if post_ui_amount > pre_ui_amount:
                        results.append({
                            'signature': signa,
                            'token_name' : token_name,
                            'token_symbol' : token_symbol,
                            'token_address': token_address,
                            # 'token_price' : calculated_pump_token_price,
                            'pre_amount': pre_ui_amount,
                            'post_amount': post_ui_amount,
                            'buy(Token)': difference,
                            'sell(Sol)' : sol_balance,
                            'on' : where
                        })
                    elif pre_ui_amount > post_ui_amount:
                        results.append({
                            'signature': signa,
                            'token_name' : token_name,
                            'token_symbol' : token_symbol,
                            'token_address': token_address,
                            # 'token_price' : calculated_pump_token_price,
                            'pre_amount': pre_ui_amount,
                            'post_amount': post_ui_amount,
                            'sell(Token)': difference,
                            'buy(Sol)' : sol_balance,
                            'on' : where
                        })
                else:
                    
                    results.append({
                            'signature': signa,
                            'token_name' : token_name,
                            'token_symbol' : token_symbol,
                            'token_address': token_address,
                            # 'token_price' : calculated_pump_token_price,
                            'pre_amount': 0,
                            'post_amount': post_ui_amount,
                            'buy(Token)': post_ui_amount,
                            'sell(Sol)' : sol_balance,
                            'on' : 'Pump'
                        })
                

    return results

if __name__ == "__main__" :
    SignatureList = []
    finalData = []
    finalresult = []
    walletaddress = WALLET_ADDRESS
    SignatureList = get_Signaturelist(walletaddress)
 
    
    for oneSignature in SignatureList:
        oneTransaction = get_transaction(oneSignature)
        if len(finalData) < 500:
            tokenInforBuySellAmount = get_tokens_balances(WALLET_ADDRESS, oneTransaction, oneSignature)
            if tokenInforBuySellAmount:
                print(tokenInforBuySellAmount)
                finalData.append(tokenInforBuySellAmount)
                update_final_result(tokenInforBuySellAmount, finalresult)
                
        else:
            break
    print("\n")
    print("This is Final reports")
    print("\n")
    print(finalresult)    
    with open('result.json', 'w') as json_file:
        json.dump(finalresult, json_file, indent=4)        
    
    

    # oneSignature = "42185AwYQehkh7iQkQ5ehRSkcmrvhRgmeetFiVjcQv4VK9uVRC7AZ4uVJSgBkfr7qCZs5BrJvBnJHfKL4MpCsdtG"
    # print("42185AwYQehkh7iQkQ5ehRSkcmrvhRgmeetFiVjcQv4VK9uVRC7AZ4uVJSgBkfr7qCZs5BrJvBnJHfKL4MpCsdtG")
    # oneTransaction = get_transaction(oneSignature)
    # # # # tokenInforBuySellAmount = get_tokens_balances(WALLET_ADDRESS, oneTransaction, oneSignature)
    # # # pair_address = oneTransaction.get('result', {}).get('transaction', {}).get('message', {}).get('accountKeys', [])
    # # # pair_address1 = pair_address[5]['pubkey']
    # # # pair_address2 = pair_address[6]['pubkey']
    # # # print("baseVault : ", pair_address1)    
    # # # print("quoteVault : ",pair_address2)
    # print(oneTransaction)
    
    
    