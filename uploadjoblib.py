from web3 import Web3
import os
import json
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration
GANACHE_URL = os.getenv('GANACHE_URL', 'http://127.0.0.1:8545')
CONTRACT_ADDRESS = "0xD1c385df99CdFf7BA3CcAa30CB0085beA8bc75Ec"  # À remplacer après déploiement
PRIVATE_KEY = "0x08719b5cb0f15027f67f9b6bed977b81b0463604f09b9f1e7dcf203a467ddcfd"  # Clé privée d'un compte Ganache
JOBLIB_FILE = 'random_forest_rules.joblib'
#CONTRACT_ABI = json.load(open('~/Desktop/pfa/NSL-KDD-Network-Intrusion-Detection/blockchain/build/contracts/JoblibStorage.json'))['abi']
CONTRACT_ABI = [
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "bytes32",
          "name": "fileHash",
          "type": "bytes32"
        },
        {
          "indexed": True,
          "internalType": "address",
          "name": "uploader",
          "type": "address"
        }
      ],
      "name": "FileStored",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "fileHashes",
      "outputs": [
        {
          "internalType": "bytes32",
          "name": "",
          "type": "bytes32"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    },
    {
      "inputs": [
        {
          "internalType": "bytes32",
          "name": "",
          "type": "bytes32"
        }
      ],
      "name": "files",
      "outputs": [
        {
          "internalType": "bytes32",
          "name": "fileHash",
          "type": "bytes32"
        },
        {
          "internalType": "uint256",
          "name": "size",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "timestamp",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "uploader",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    },
    {
      "inputs": [
        {
          "internalType": "bytes32",
          "name": "fileHash",
          "type": "bytes32"
        },
        {
          "internalType": "uint256",
          "name": "size",
          "type": "uint256"
        }
      ],
      "name": "storeFile",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getFileCount",
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
"""  
def main():
    # Initialiser Web3
    w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
    
    if not w3.is_connected():
        raise ConnectionError("Impossible de se connecter à Ganache")

    # Préparer le compte
    account = w3.eth.account.from_key(PRIVATE_KEY)
    
    # Charger le contrat
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    
    # Lire le fichier .joblib
    with open(JOBLIB_FILE, 'rb') as f:
        file_data = f.read()
    
    # Calculer le hash
    file_hash = w3.keccak(file_data).hex()
    file_size = len(file_data)
    
    # Construire la transaction
    tx = contract.functions.storeFile(
        file_hash,
        file_size
    ).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 2000000,
        'gasPrice': w3.to_wei('50', 'gwei')
    })
    
    # Signer et envoyer la transaction
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    # Attendre la confirmation
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print(f"Transaction réussie: {receipt.transactionHash.hex()}")
    print(f"Hash du fichier: {file_hash}")
    print(f"Taille du fichier: {file_size} bytes")
"""
def main():
    # Initialiser Web3
    w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
    
    if not w3.is_connected():
        raise ConnectionError("Impossible de se connecter à Ganache")

    # Préparer le compte
    account = w3.eth.account.from_key(PRIVATE_KEY)
    
    # Charger le contrat
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    
    # Lire le fichier .joblib
    with open(JOBLIB_FILE, 'rb') as f:
        file_data = f.read()
    
    # Calculer le hash (keep as bytes, don't convert to hex)
    file_hash = w3.keccak(file_data)  # Remove .hex() here
    file_size = len(file_data)
    
    # Construire la transaction
    tx = contract.functions.storeFile(
        file_hash,  # Now passing bytes directly
        file_size
    ).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 2000000,
        'gasPrice': w3.to_wei('50', 'gwei')
    })
    
    # Signer et envoyer la transaction
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    # Attendre la confirmation
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print(f"Transaction réussie: {receipt.transactionHash.hex()}")
    print(f"Hash du fichier: {file_hash.hex()}")  # Can convert to hex for display
    print(f"Taille du fichier: {file_size} bytes")
if __name__ == "__main__":
    main()