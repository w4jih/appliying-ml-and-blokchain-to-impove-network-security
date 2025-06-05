"""from web3 import Web3
import json

# --- Connect to Ganache ---
ganache_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Check connection
if not web3.is_connected():
    raise Exception("Cannot connect to Ganache")

# Set default account (you can change the index if needed)
web3.eth.default_account = web3.eth.accounts[0]

# --- Load Contract ABI and Address ---
with open('build/contracts/RandomForestRules.json') as f:
    contract_json = json.load(f)
    abi = contract_json['abi']
    # Replace this with the actual deployed address after migration
    contract_address = "0x7869ECEdf65c7670D95225A927AA9B2dd7013c71"

contract = web3.eth.contract(address=contract_address, abi=abi)

# --- Read and Upload Rules ---
def upload_rules(file_path):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file if line.strip()]
    
    for line in lines:
        tx_hash = contract.functions.addRule(line).transact()
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Uploaded rule: {line}")

    total = contract.functions.getRuleCount().call()
    print(f"Total rules uploaded: {total}")

if __name__ == "__main__":
    upload_rules("random_forest_rules.txt")
"""





from web3 import Web3

# --- Connect to Ganache ---
ganache_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Check connection
if not web3.is_connected():
    raise Exception("Cannot connect to Ganache at " + ganache_url)

# Set default account (you can change the index if needed)
accounts = web3.eth.accounts
if not accounts:
    raise Exception("No accounts found on the node; is Ganache running unlocked?")
web3.eth.default_account = accounts[0]

# --- Manually paste your ABI here ---
abi = [
    {
      "inputs": [],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "content",
          "type": "string"
        }
      ],
      "name": "RuleAdded",
      "type": "event"
    },
    {
      "inputs": [],
      "name": "owner",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    },
    {
      "inputs": [],
      "name": "ruleCount",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "rules",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        },
        {
          "internalType": "string",
          "name": "content",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_content",
          "type": "string"
        }
      ],
      "name": "addRule",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_id",
          "type": "uint256"
        }
      ],
      "name": "getRule",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    },
    {
      "inputs": [],
      "name": "getRuleCount",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    }
  ]
# --- Set your deployed contract address here ---
contract_address = "0x0cC5bE6513a41a4C3492BAca918659E24aD870bC"
contract = web3.eth.contract(address=contract_address, abi=abi)

# --- Read and Upload Rules ---
def upload_rules(file_path: str):
    try:
        with open(file_path, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        raise FileNotFoundError(f"Rules file not found: {file_path}")

    for line in lines:
        tx_hash = contract.functions.addRule(line).transact()
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Uploaded rule: {line}")

    total = contract.functions.getRuleCount().call()
    print(f"Total rules uploaded: {total}")

if __name__ == "__main__":
    upload_rules("certain_rules.txt")
