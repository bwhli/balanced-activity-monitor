import os
import requests
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from icx import Icx
from processor import process_transaction
from rich import print
from time import sleep
from utils import filter_transactions

load_dotenv()


# Initialize environment variables.
ENV = os.getenv("ENV")


def main():
    # Initialize start block.
    if ENV == "DEBUG":
        latest_block = 45617893
    else:
        latest_block = Icx().get_latest_block()

    print(f"Initializing with Block {latest_block}...")

    while True:
        try:
            while True:
                url = f"https://tracker.icon.community/api/v1/transactions/block-number/{latest_block}?limit=100"
                r = requests.get(url)
                r.raise_for_status()
                transactions = r.json()
                if len(transactions) > 0:
                    filtered_transactions = filter_transactions(transactions)
                    if len(filtered_transactions) > 0:
                        with ThreadPoolExecutor(max_workers=len(filtered_transactions)) as executor:
                            for tx in filtered_transactions:
                                executor.submit(process_transaction, tx=tx)
                    break
                else:
                    sleep(1)
                    continue
        except Exception as e:
            print(e)
            continue
        else:
            if ENV == "DEBUG":
                return
            print(f"Processed Block {latest_block}")
            latest_block += 1
            continue


if __name__ == "__main__":
    main()
