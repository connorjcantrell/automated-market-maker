import os
from algosdk.v2client import algod
from tinyman.v1.client import TinymanTestnetClient

class AlgodTestnetClient:
    def __init__():
        """Instantiate and return Algod client object""" 
        algod_address = "https://testnet-algorand.api.purestake.io/ps2"
        algod_token = os.environ(['PURESTAKE_API_TOKEN'])
        headers = {
            "X-API-Key": algod_token,
        }
        return algod.AlgodClient(algod_token, algod_address, headers)