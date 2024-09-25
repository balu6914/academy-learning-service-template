# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2024 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This module contains the handlers for the skill of LearningAbciApp."""

import requests
import os  # To load environment variables
from web3 import Web3  # For Ethereum transaction
from aea.skills.base import Handler
from packages.valory.skills.abstract_round_abci.handlers import (
    ABCIRoundHandler as BaseABCIRoundHandler,
)
from packages.valory.skills.abstract_round_abci.handlers import (
    ContractApiHandler as BaseContractApiHandler,
)
from packages.valory.skills.abstract_round_abci.handlers import (
    HttpHandler as BaseHttpHandler,
)
from packages.valory.skills.abstract_round_abci.handlers import (
    IpfsHandler as BaseIpfsHandler,
)
from packages.valory.skills.abstract_round_abci.handlers import (
    LedgerApiHandler as BaseLedgerApiHandler,
)
from packages.valory.skills.abstract_round_abci.handlers import (
    SigningHandler as BaseSigningHandler,
)
from packages.valory.skills.abstract_round_abci.handlers import (
    TendermintHandler as BaseTendermintHandler,
)

# Existing handlers
ABCIHandler = BaseABCIRoundHandler
HttpHandler = BaseHttpHandler
SigningHandler = BaseSigningHandler
LedgerApiHandler = BaseLedgerApiHandler
ContractApiHandler = BaseContractApiHandler
TendermintHandler = BaseTendermintHandler
IpfsHandler = BaseIpfsHandler

# New API Call and Transaction Handler
class APIHandler(Handler):
    """Handler to make an external API call and send transactions."""

    def setup(self):
        """Setup the handler."""
        self.web3 = Web3(Web3.HTTPProvider(os.getenv("ETHEREUM_RPC_URL")))
        self.private_key = os.getenv("ETHEREUM_PRIVATE_KEY")
        self.safe_contract_address = os.getenv("SAFE_CONTRACT_ADDRESS")

    def send_transaction(self):
        """Send a standard transaction to the Ethereum blockchain."""
        try:
            account = self.web3.eth.account.privateKeyToAccount(self.private_key)
            tx = {
                "to": "0x7743973Fe6B36500C1e1aADe0A3fe7EE9654e8a4",  # The recipient Ethereum address
                "value": self.web3.toWei(0.01, "ether"),  # Sending 0.01 ether
                "gas": 21000,
                "gasPrice": self.web3.toWei("50", "gwei"),
                "nonce": self.web3.eth.getTransactionCount(account.address),
            }

            signed_tx = self.web3.eth.account.signTransaction(tx, private_key=self.private_key)
            tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
            print(f"Transaction sent: {tx_hash.hex()}")
        except Exception as e:
            print(f"Error during transaction: {e}")

    def send_safe_eth_transfer(self):
        """Send ETH to the Gnosis Safe contract."""
        try:
            account = self.web3.eth.account.privateKeyToAccount(self.private_key)
            tx = {
                "to": self.safe_contract_address,  # The Gnosis Safe contract address
                "value": self.web3.toWei(0.01, "ether"),  # Sending 0.01 ether
                "gas": 21000,
                "gasPrice": self.web3.toWei("50", "gwei"),
                "nonce": self.web3.eth.getTransactionCount(account.address),
            }

            signed_tx = self.web3.eth.account.signTransaction(tx, private_key=self.private_key)
            tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
            print(f"Safe ETH transfer transaction sent: {tx_hash.hex()}")
        except Exception as e:
            print(f"Error during Safe ETH transfer: {e}")

    def handle(self, message):
        """Handle incoming messages by making an API request and sending a transaction."""
        try:
            # Get the Coingecko API key from the environment
            api_key = os.getenv("COINGECKO_API_KEY")
            url = f"https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd&x_cg_pro_api_key={api_key}"

            # Example API call using the Coingecko API key
            response = requests.get(url)

            if response.status_code == 200:
                print("API call successful!")
                print(f"Ethereum price: {response.json()}")
                self.send_transaction()  # Send transaction after successful API call
                self.send_safe_eth_transfer()  # Send ETH transfer to Safe
            else:
                print(f"API call failed with status code: {response.status_code}")
        except Exception as e:
            print(f"Error during API call: {e}")
