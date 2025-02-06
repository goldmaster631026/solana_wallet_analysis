import requests
import pandas as pd
from config import API_KEY , WALLET_ADDRESS
import requests


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

def get_tokens_balances (account_address, transaction_data, signa):
    results = []
    pre_token_balances = transaction_data.get('result', {}).get('meta', {}).get('preTokenBalances', [])
    post_token_balances = transaction_data.get('result', {}).get('meta', {}).get('postTokenBalances', [])
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
                            'token_address': token_address,
                            'pre_amount': pre_ui_amount,
                            'post_amount': post_ui_amount,
                            'buy': difference,
                            'on' : where
                        })
                    elif pre_ui_amount > post_ui_amount:
                        results.append({
                            'signature': signa,
                            'token_address': token_address,
                            'pre_amount': pre_ui_amount,
                            'post_amount': post_ui_amount,
                            'sell': difference,
                            'on' : where
                        })
                else:
                    results.append({
                            'signature': signa,
                            'token_address': token_address,
                            'pre_amount': 0,
                            'post_amount': post_ui_amount,
                            'buy': post_ui_amount,
                            'on' : 'Pump'
                        })
                

    return results

if __name__ == "__main__" :
    SignatureList = []
    walletaddress = WALLET_ADDRESS
    SignatureList = get_Signaturelist(walletaddress)
 
    
    for oneSignature in SignatureList:
        oneTransaction = get_transaction(oneSignature)
        tokenInforBuySellAmount = get_tokens_balances(WALLET_ADDRESS, oneTransaction, oneSignature)
        if tokenInforBuySellAmount:
            print(tokenInforBuySellAmount)
    
    

    # oneSignature = "64sYz36LLLGnMSDFyDbLW6rYLJxcA57hVD5HivriLkFNrXw4LTu2pheJchdZ57LvbMSvNgV1PskR3gkhhFMTvhGU"
    # print("64sYz36LLLGnMSDFyDbLW6rYLJxcA57hVD5HivriLkFNrXw4LTu2pheJchdZ57LvbMSvNgV1PskR3gkhhFMTvhGU")
    # oneTransaction = get_transaction(oneSignature)
    # print(oneTransaction)