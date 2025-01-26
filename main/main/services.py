# from web3 import Web3
# import json
# from django.conf import settings
#
# # Connect to the local Hardhat blockchain
# web3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_URL))
#
# # Load contract details
# with open("home/abi.json") as f:
#     contract_abi = json.load(f)
#
# contract = web3.eth.contract(
#     address=settings.CONTRACT_ADDRESS, abi=contract_abi
# )
#
# def set_data(value, account, private_key):
#     tx = contract.functions.set(value).buildTransaction({
#         'from': account,
#         'nonce': web3.eth.getTransactionCount(account),
#         'gas': 2000000,
#         'gasPrice': web3.toWei('50', 'gwei'),
#     })
#     signed_tx = web3.eth.account.sign_transaction(tx, private_key)
#     tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
#     return web3.eth.waitForTransactionReceipt(tx_hash)
#
# def get_data():
#     return contract.functions.get().call()
