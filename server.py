
from flask import Flask, request, jsonify
from web3 import Web3

app = Flask(__name__)

# --- Web3 + Contract Setup ---
ganache_url = "http://127.0.0.1:8545"  # adjust if your Ganache is on a different port
web3 = Web3(Web3.HTTPProvider(ganache_url))

if not web3.is_connected():
    raise Exception(f"Cannot connect to Ganache at {ganache_url}")

accounts = web3.eth.accounts
if not accounts:
    raise Exception("No accounts found on the node; is Ganache running?")

web3.eth.default_account = accounts[0]

# ── Paste your contract's ABI here ────────────────────────────────────────────────
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
# ──────────────────────────────────────────────────────────────────────────────

# ── Replace this with your deployed contract address ────────────────────────────
contract_address = "0x7869ECEdf65c7670D95225A927AA9B2dd7013c71"
# ──────────────────────────────────────────────────────────────────────────────

contract = web3.eth.contract(address=contract_address, abi=abi)


def load_continuous_rules_from_chain():
    """
    Fetch all rules stored in the RandomForestRules contract.
    Returns a Python list of strings.
    """
    rules = []
    try:
        total_count = contract.functions.getRuleCount().call()
    except Exception as e:
        raise Exception(f"Error reading rule count from chain: {e}")

    for i in range(total_count):
        try:
            rule_str = contract.functions.getRule(i).call()
        except Exception as e:
            # If a call fails, skip that index (or choose to abort)
            print(f"Warning: could not fetch rule {i}: {e}")
            continue
        # Only append non-empty rules
        if rule_str and rule_str.strip():
            rules.append(rule_str.strip())

    return rules


# Load once at startup
CONTINUOUS_RULES = load_continuous_rules_from_chain()
print(f"{len(CONTINUOUS_RULES)} règles continues chargées depuis la blockchain")


@app.route('/correct_rules', methods=['POST'])
def correct_rules():
    """
    Expects JSON body with key "uncertain_rules": a list of rule‐strings.
    Returns JSON with "corrected_rules": a list of matching continuous rules.
    """
    data = request.get_json() or {}
    uncertain_rules = data.get('uncertain_rules', [])
    corrected = []

    for ur in uncertain_rules:
        # Extract the "condition" part (everything before " then", if present)
        cond_ur = ur.split(" then")[0].strip()
        for cr in CONTINUOUS_RULES:
            if cr.startswith(cond_ur):
                corrected.append(cr)

    return jsonify({"corrected_rules": corrected})


if __name__ == '__main__':
    # Use debug=False in production
    app.run(host='0.0.0.0', port=5000)
