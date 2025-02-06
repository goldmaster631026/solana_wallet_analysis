import requests
import pandas as pd
from config import API_KEY
import requests


def get_Signaturelist(walletaddress) :
    
    response = requests.post(
        "https://mainnet.helius-rpc.com/?api-key=97f3ea30-7f8b-4c10-a368-1160df74ed5b",
        headers={"Content-Type":"application/json"},
        json={"jsonrpc":"2.0","id":"1","method":"getSignaturesForAddress","params":[walletaddress]}
    )
    data = response.json()
    # Initialize an empty list to store signatures
    SignList = []

    # Check if 'result' is present in the data and is a list
    if 'result' in data and isinstance(data['result'], list):
        # Loop through each item in the result list
        for item in data['result']:
            # Check if 'signature' key exists in the item
            if 'signature' in item:
                # Append the signature value to SignList
                SignList.append(item['signature'])

    # Print the extracted signatures
    print(SignList)
    
def get_transaction (signature) :
    
    return True



# print(data)
if __name__ == "__main__" :
    walletaddress = input("Input wallet address : ")
    get_Signaturelist(walletaddress)