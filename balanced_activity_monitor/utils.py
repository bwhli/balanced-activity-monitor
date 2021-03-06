import codecs
from models import Tx
import os
import requests
from functools import lru_cache

ENV = os.getenv("ENV")

CONTRACTS = {
    "cxa0af3165c08318e988cb30993b3048335b94af6c": "Balanced DEX",
    "cx66d4d90f5f113eba575bf793570135f9b10cece1": "Balanced Loans",
    "cx203d9cd2a669be67177e997b8948ce2c35caffae": "Balanced Dividends",
    "cx44250a12074799e26fdeee75648ae47e2cc84219": "Balanced Governance",
    "cxf58b9a1898998a31be7f1d99276204a3333ac9b3": "Balanced Reserve Fund",
    "cx43e2eec79eb76293c298f2b17aec06097be606e0": "Balanced Staking",
    "cx835b300dcfe01f0bdb794e134a0c5628384f4367": "Balanced DAO Fund",
    "cx10d59e8103ab44635190bd4139dbfd682fa2d07e": "Balanced Rewards",
    "cx40d59439571299bca40362db2a7d8cae5b0b30b0": "Balanced Rebalance",
    "cx21e94c08c03daee80c25d8ee3ea22a20786ec231": "Balanced Router",
    "cxcfe9d1f83fa871e903008471cca786662437e58d": "Balanced Worker Token",
}

TOKENS = {
    "cxf61cd5a45dc9f91c15aa65831a30a90d59a09619": {"ticker": "BALN", "precision": 18},
    "cx88fd7df7ddff82f7cc735c871dc519838cb235bb": {"ticker": "bnUSD", "precision": 18},
    "cx2e6d0fc0eca04965d06038c8406093337f085fcf": {"ticker": "CFT", "precision": 18},
    "cx785d504f44b5d2c8dac04c5a1ecd75f18ee57d16": {"ticker": "FIN", "precision": 18},
    "cx6139a27c15f1653471ffba0b4b88dc15de7e3267": {"ticker": "GBET", "precision": 18},
    "cxe7c05b43b3832c04735e7f109409ebcb9c19e664": {"ticker": "IAM", "precision": 18},
    "cxae3034235540b924dfcc1b45836c293dcc82bfb7": {"ticker": "IUSDC", "precision": 6},
    "cx3a36ea1f6b9aa3d2dd9cb68e8987bcc3aabaaa88": {"ticker": "IUSDT", "precision": 6},
    "cx369a5f4ce4f4648dfc96ba0c8229be0693b4eca2": {"ticker": "METX", "precision": 18},
    "cx1a29259a59f463a67bb2ef84398b30ca56b5830a": {"ticker": "OMM", "precision": 18},
    "cx2609b924e33ef00b648a409245c7ea394c467824": {"ticker": "sICX", "precision": 18},
    "cxbb2871f468a3008f80b08fdde5b8b951583acf06": {"ticker": "USDS", "precision": 18},
}

IGNORED_CONTRACTS = ["cxaa99a164586883eed0322d62a31946dfa9491fa6"]  # [Optimus]

#####################
## CONTRACTS STUFF ##
#####################


@lru_cache(maxsize=1)
def get_subscribed_contracts():
    contracts = list(CONTRACTS.keys())
    tokens = list(TOKENS.keys())
    return contracts + tokens


#################
## TOKEN STUFF ##
#################


def get_token_ticker(contract: str):
    if contract is None or contract == "None":
        return "ICX"
    else:
        return TOKENS[contract]["ticker"]


def get_token_precision(contract: str):
    if contract[:2] != "cx":
        contract = get_token_contract(contract)
    if contract is None or contract == "None":
        return 18
    else:
        return TOKENS[contract]["precision"]


def get_token_contract(ticker: str):
    for k, v in TOKENS.items():
        if v["ticker"] == ticker:
            return k


@lru_cache(maxsize=1)
def get_token_contracts():
    return list(TOKENS.keys())


#####################
## TEXT FORMATTING ##
#####################


def comma_separator(sequence):
    if len(sequence) > 1:
        return "{}, and {}".format(", ".join(sequence[:-1]), sequence[-1])


def decode_hex_string(input):
    if input[:2] == "0x":
        input = input[2:]
    result = codecs.decode(input, "hex").decode("utf-8")
    print(result)
    return result


def format_token(token_amount: int, token_contract: str):
    if token_contract[:2] != "cx":
        token_contract = get_token_contract(token_contract)
    token_symbol = get_token_ticker(token_contract)
    token_precision = get_token_precision(token_contract)
    token_amount = token_amount / 10 ** token_precision
    if token_amount.is_integer() is True:
        result = f"{token_amount:,.{0}f} {token_symbol}"
    else:
        result = f"{token_amount:,.{4}f} {token_symbol}"
    return result


def hex_to_int(input):
    result = int(input, 16)
    return result


###################
## DISCORD STUFF ##
###################


def send_discord_notification(message: tuple, from_address: str, tx_hash: str, url: None):
    if url is None:
        url = f"https://tracker.icon.community/transaction/{tx_hash}"
    emoji, body = message[0], message[1]
    formatted_message = f"{emoji} `{from_address[:4]}...{from_address[-4:]}`  [**{body}**](<{url}>)."
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
    payload = {
        "username": "Balanced Activity Monitor",
        "avatar_url": "https://brianli.com/balanced/balanced-dao.png",
        "content": formatted_message,
    }
    r = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if r.status_code == 204:
        print("Message Delivered!")
    else:
        print("Message Not Delivered!")


##################
## MISC UTILITY ##
##################


def filter_transactions(transactions: list):
    return [
        Tx(**tx) for tx in transactions if tx["status"] == "0x1" and tx["to_address"] in get_subscribed_contracts()
    ]
