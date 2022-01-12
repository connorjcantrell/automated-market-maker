from algosdk.error import AlgodHTTPError
from algosdk.future.transaction import wait_for_confirmation
from clients import AlgodTestnetClient, TinymanTestnetClient

class AMMClient:
    """Automated Market Maker Client"""
    def __init__(self, user_address, private_key):
        self.tinyman_client = TinymanTestnetClient(user_address=user_address)
        self.algod_client = AlgodTestnetClient()
        self.user_address = user_address
        self.private_key = private_key

    def swap(
        self,
        amount,
        asset_id,
        slippage_percentage=0.01,
    ):
        if(not self.tinyman_client.is_opted_in):
            self.app_optin()
            
        if not self.tinyman_client.asset_is_opted_in(asset_id):
            self.asset_optin(asset_id)

        ASA = self.tinyman_client.fetch_asset(asset_id)
        ALGO = self.tinyman_client.fetch_asset(0)
        
        pool = self.tinyman_client.fetch_pool(ASA, ALGO)

        quote = self.get_quote(pool, ALGO(amount), slippage_percentage)

        txn_group = self.prepare_swap_transaction(quote, pool)
        txn_group = self.submit_transaction(txn_group)

        self.redeem_excess_amount(pool, ASA)


    def app_optin(self):
        txn_group = self.algod_client.prepare_app_optin_transactions()
        txn_group.sign_with_private_key(self.user_address, self.private_key)
        self.submit_transaction(txn_group)
        

    def asset_optin(self, asset_id):
        txn_group = self.tinyman_client.prepare_asset_optin_transactions(asset_id)
        txn_group.sign_with_private_key(self.user_address, self.private_key)
        self.submit_transaction(txn_group)


    def get_quote(self, pool, asset_amount, slipagge):
        return pool.fetch_fixed_input_swap_quote(asset_amount, slipagge)


    def prepare_swap_transaction(self, quote, pool):
        txn_group = pool.prepare_swap_transactions_from_quote(quote)
        txn_group.sign_with_private_key(self.user_address, self.private_key)
        self.submit_transaction(txn_group)
        return txn_group


    def submit_transaction(self, txn_group):
        try:
            txid = self.algod_client.send_transactions(txn_group.signed_transactions)
        except AlgodHTTPError as e:
            return str(e)
        return wait_for_confirmation(self.algod_client, txid, 10)


    def redeem_excess_amount(self, pool, asset):
        excess = pool.fetch_excess_amounts()
        if asset in excess:
            amount = excess[asset]
            txn_group = pool.prepare_redeem_transactions(amount)
            txn_group.sign_with_private_key(self.user_address, self.private_key)
            result = self.tinyman_client.submit(txn_group, wait=True)
            return result
                