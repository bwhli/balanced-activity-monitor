from functools import lru_cache
import requests
from rich import print
from time import sleep

__version__ = "0.1.0"


@lru_cache(maxsize=1)
def build_token_list():
    print("Building token list...")
    token_list = []
    token_dict = {}
    i = 0
    while i >= 0:
        url = f"https://tracker.icon.community/api/v1/contracts?limit=100&skip={100 * i}&contract_type=IRC2"
        print(url)
        r = requests.get(url)
        tokens = r.json()
        if len(tokens) == 0:
            break
        else:
            for token in tokens:
                token_list.append(token)
        sleep(0.1)
        i += 1
    for token in token_list:
        contract = token["address"]
        precision = int(token["decimals"], 16)
        ticker = token["symbol"]
        token_dict[contract] = {"ticker": ticker, "precision": precision}
    return token_dict
