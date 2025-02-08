import requests
import pandas as pd
from config import API_KEY , WALLET_ADDRESS
import requests, json
from moralis import sol_api
from solders.pubkey import Pubkey
from construct import Struct, Int64ul
from solana.rpc.api import Client

RPC = "https://api.mainnet-beta.solana.com"  # Replace with your RPC endpoint
client = Client(RPC)

def get_bonding_curve_data(bonding_curve_address: str):
    """
    Fetches and parses bonding curve data from a Solana account.
    """
    try:
        bonding_curve_pubkey = Pubkey.from_string(bonding_curve_address)
        account_info = client.get_account_info(bonding_curve_pubkey)

        if not account_info.value:
            print(f"No account data available for {bonding_curve_address}")
            return None

        data = account_info.value.data
        if not data:
            print(f"No data in account {bonding_curve_address}")
            return None

        # Define the structure of the bonding curve data
        bonding_curve_struct = Struct(
            "virtualTokenReserves" / Int64ul,
            "virtualSolReserves" / Int64ul,
            "realTokenReserves" / Int64ul,
            "realSolReserves" / Int64ul,
            "tokenTotalSupply" / Int64ul
        )

        # Parse the account data
        parsed_data = bonding_curve_struct.parse(bytes(data))
        return parsed_data
    except Exception as e:
        print(f"Error fetching or parsing data: {e}")
        return None

# Example usage:
bonding_curve_address = "63ooTk2JDjbqnuBjrCFx5BDUqv5eitvNUWJ8UpZXeuWi"  # Replace with the actual address
data = get_bonding_curve_data(bonding_curve_address)

if data:
    print("Bonding Curve Data:")
    print(f"  Virtual Token Reserves: {data.virtualTokenReserves}")
    print(f"  Virtual SOL Reserves: {data.virtualSolReserves}")
    print(f"  Real Token Reserves: {data.realTokenReserves}")
    print(f"  Real SOL Reserves: {data.realSolReserves}")
    print(f"  Token Total Supply: {data.tokenTotalSupply}")
else:
    print("Could not retrieve bonding curve data.")


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
                # print(token_name)
                
                
                where = "Pump" if search_substring(transaction_data, '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P') else "Swap"

                # post_ui_amount = post_balance['uiTokenAmount']['uiAmount'] possible also
                # post_ui_amount = post_balance['uiTokenAmount'].get('uiAmount', 0)
                
                
                # Raydium token price calculate start ==========
                # if  where != "Pump" :
                #     pair_address = oneTransaction.get('result', {}).get('transaction', {}).get('message', {}).get('accountKeys', [])
                #     pair_address1 = pair_address[5]['pubkey']
                #     pair_address2 = pair_address[6]['pubkey']
                #     print("baseVault : ", pair_address1)    
                #     print("quoteVault : ",pair_address2)
                    
                #     response = requests.post(
                #     "https://mainnet.helius-rpc.com/?api-key=97f3ea30-7f8b-4c10-a368-1160df74ed5b",
                #     headers={"Content-Type":"application/json"},
                #     json={"jsonrpc":"2.0","id":1,"method":"getTokenAccountBalance","params":[pair_address1]}
                #     )
                #     pair_address1_data = response.json()
                #     flag = 1 if pair_address1_data['result']['value']['uiAmount'] else 0
                #     if flag == 1 :
                #         baseamount = pair_address1_data['result']['value']['uiAmount']
                #     response = requests.post(
                #     "https://mainnet.helius-rpc.com/?api-key=97f3ea30-7f8b-4c10-a368-1160df74ed5b",
                #     headers={"Content-Type":"application/json"},
                #     json={"jsonrpc":"2.0","id":1,"method":"getTokenAccountBalance","params":[pair_address2]}
                #     )
                #     pair_address2_data = response.json()
                #     flag = 1 if pair_address2_data['result']['value']['amount'] else 0
                #     if flag == 1 :
                #         quoteamount = pair_address2_data['result']['value']['amount']
                
                #     # print(baseamount)
                #     # print(quoteamount)
                #     raydium_token_price = (int(quoteamount)) / 1000000000 / (float(baseamount))
                #     print("calculated" , raydium_token_price)
            
                
                # Raydium token price calculate End ============
                
# sol - 3
# token - 4
                # Pump fun token price calculate start ============
                if where == "Pump" :
                    pair_address = oneTransaction.get('result', {}).get('transaction', {}).get('message', {}).get('accountKeys', [])
                    pair_address = pair_address[2]['pubkey']
                    print(pair_address)
                    
                
                # Pump fun token price calculate end ==============
                
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
                            # 'token_price' : raydium_token_price,
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
                            # 'token_price' : raydium_token_price,
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
                            # 'token_price' : raydium_token_price,
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
 
    
    # for oneSignature in SignatureList:
    #     oneTransaction = get_transaction(oneSignature)
    #     if len(finalData) < 20:
    #         tokenInforBuySellAmount = get_tokens_balances(WALLET_ADDRESS, oneTransaction, oneSignature)
    #         if tokenInforBuySellAmount:
    #             print(tokenInforBuySellAmount)
    #             finalData.append(tokenInforBuySellAmount)
    #             update_final_result(tokenInforBuySellAmount, finalresult)
                
    #     else:
    #         break
    # print("\n")
    # print("This is Final reports")
    # print("\n")
    # print(finalresult)    
    # with open('result.json', 'w') as json_file:
    #     json.dump(finalresult, json_file, indent=4)        
    
    

    oneSignature = "4dJpcadfwQo4GuPPW1VVEeCLShCaz4poGAhypPqem5uH2VVQkpFbR1KaMefVtydiXv4v8Q1uWqzWcb2zZu1ZQZNf"
    print("4dJpcadfwQo4GuPPW1VVEeCLShCaz4poGAhypPqem5uH2VVQkpFbR1KaMefVtydiXv4v8Q1uWqzWcb2zZu1ZQZNf")
    oneTransaction = get_transaction(oneSignature)
    # # tokenInforBuySellAmount = get_tokens_balances(WALLET_ADDRESS, oneTransaction, oneSignature)
    # pair_address = oneTransaction.get('result', {}).get('transaction', {}).get('message', {}).get('accountKeys', [])
    # pair_address1 = pair_address[5]['pubkey']
    # pair_address2 = pair_address[6]['pubkey']
    # print("baseVault : ", pair_address1)    
    # print("quoteVault : ",pair_address2)
    print(oneTransaction)
    
    
    