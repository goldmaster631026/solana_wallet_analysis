import requests
import pandas as pd
from config import API_KEY , WALLET_ADDRESS
import requests, json


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
def update_final_result( new_item, finalresult):
    token_address = new_item[0]['token_address']
    token_name = new_item[0]['token_name']
    token_symbol = new_item[0]['token_symbol']
    buy_amount = new_item[0].get('buy(Token)', 0)
    sell_amount = new_item[0].get('sell(Token)', 0)
    sol_buy = new_item[0].get('sell(Sol)', 0)
    sol_sell = new_item[0].get('buy(Sol)', 0)

    for item in finalresult:
        if item['token_address'] == token_address:
            # Found existing token_address, update buy and sell
            item['buy(Token)'] = item.get('buy(Token)', 0) + buy_amount
            item['sell(Token)'] = item.get('sell(Token)', 0) + sell_amount
            item['sol_buy'] = item.get('sol_buy', 0) + sol_buy
            item['sol_sell'] = item.get('sol_sell', 0) + sol_sell
            item['sol_profit'] = item.get('sol_sell') - item.get('sol_buy')
            item['profit_%'] = (item.get('sol_profit')/ item.get('sol_buy')) * 100
           
            return

    # If token_address is not found, add a new entry with buy and sell
    finalresult.append({
        'token_name' : token_name,
        'token_symbol' : token_symbol,
        'token_address': token_address,
        'buy(Token)': buy_amount,
        'sell(Token)': sell_amount,
        'sol_buy' : sol_buy,
        'sol_sell' : sol_sell,
        'sol_profit' : sol_sell - sol_buy,
        'profit_%' : 'NA'
        
        
    })
    
def get_tokens_balances (account_address, transaction_data, signa):
    results = []
    response = requests.post(
        "https://mainnet.helius-rpc.com/?api-key=97f3ea30-7f8b-4c10-a368-1160df74ed5b",
        headers={"Content-Type":"application/json"},
        json={"jsonrpc":"2.0","id":"test","method":"getAssetBatch","params":{"ids":["Gx2Uf4fmxuo1hjoRnCiNh8vLKPSY2zYYv52MXFU7R6TZ"]}}
    )
    data = response.json()
    parsed_data = json.loads(json.dumps(data))
    token_name = parsed_data['result'][0]['content']['metadata']['name']
    token_symbol = parsed_data['result'][0]['content']['metadata']['symbol']
    # print(token_name)
    
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
                where = "Pump" if search_substring(transaction_data, '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P') else "Swap"
                # where = "Pump" if "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P" in transaction_data else "Swap"
                # post_ui_amount = post_balance['uiTokenAmount']['uiAmount'] possible also
                # post_ui_amount = post_balance['uiTokenAmount'].get('uiAmount', 0)
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
    #     if len(finalData) < 5:
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
    
    

    # oneSignature = "4ni49UmSEyzUdk7ZMeVAxCESEEVytJv99cZ6d4DKHSbC6fRNofK7LERi24ZSm47sewjTskxdgZtCvcKMVvq2jDGB"
    # print("4ni49UmSEyzUdk7ZMeVAxCESEEVytJv99cZ6d4DKHSbC6fRNofK7LERi24ZSm47sewjTskxdgZtCvcKMVvq2jDGB")
    # oneTransaction = get_transaction(oneSignature)
    # tokenInforBuySellAmount = get_tokens_balances(WALLET_ADDRESS, oneTransaction, oneSignature)
    # print(oneTransaction)