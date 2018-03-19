import datetime as dt
import time
import sys
import phx_abi
custom_abi = phx_abi.get_abi()

from web3 import HTTPProvider, Web3
from web3.auto import w3

class PhxWallet(object):

    def __init__(self, args):
        self.priv_key = args['priv_key']
        self.pub_key = args['pub_key']
        self.mine_only = args['mine_only']
        self.web3_obj = Web3(HTTPProvider(args['provider']))
        self.min_withdraw = self.web3_obj.toWei(args['min_withdraw'], 'ether')
        self.min_reinvest = self.web3_obj.toWei(args['min_reinvest'], 'ether')
        self.ethphoenix   = self.web3_obj.eth.contract(address='0x2Fa0ac498D01632f959D3C18E38f4390B005e200', abi=custom_abi)
        self.phoenixcoin  = self.web3_obj.eth.contract(address='0x14b759A158879B133710f4059d32565b4a66140C', abi=custom_abi)

        ### check that the wallet has EPX
        epx_bal = self.ethphoenix.functions.tokenBalance(self.pub_key).call()
        if (epx_bal == 0):
            sys.exit('ERROR: This wallet has no EPX: %s' % self.pub_key)

        self.eth_bal  = self.web3_obj.eth.getBalance(self.pub_key)
        self.div_bal = self.web3_obj.fromWei(self.ethphoenix.functions.dividends(self.pub_key).call(), 'ether')
        self.mining_dt = None
        self.set_mining_dt()

    def update_eth_bal(self):
        self.eth_bal = self.web3_obj.eth.getBalance(self.pub_key)

    def update_div_bal(self):
        self.div_bal = self.web3_obj.fromWei(self.ethphoenix.functions.dividends(self.pub_key).call(), 'ether')

    def set_mining_dt(self):
        cooldown = self.phoenixcoin.functions.miningCooldown().call({'from': self.pub_key})
        self.mining_dt = dt.datetime.now() + dt.timedelta(seconds=int(cooldown))

    def mine(self):
        self.raw_txn('0x14b759A158879B133710f4059d32565b4a66140C','0x99f4b251')

    def withdraw_divs(self):
        self.raw_txn('0x2Fa0ac498D01632f959D3C18E38f4390B005e200','0x3ccfd60b')

    def reinvest_divs(self):
        divs_bal = self.ethphoenix.functions.dividends(self.pub_key).call()
        if (divs_bal > self.min_reinvest):
            print('\t\tMinimum reinvestment parameter reached. Reinvesting...')
            self.raw_txn('0x2Fa0ac498D01632f959D3C18E38f4390B005e200','0x957b2e56')
        else:
            print('\t\tInsufficient dividends (%f) to either withdraw or reinvest.' % self.div_bal)

    def raw_txn(self, addr, txn_data):
        nonce = self.web3_obj.eth.getTransactionCount(self.pub_key)
        gas = self.web3_obj.eth.gasPrice
        base_trans = {
            'to': addr,
            'from': self.pub_key,
            'data': txn_data,
            'gasPrice': gas,
            'chainId': 1,
            'value': 0,
            'nonce': nonce
        }
        gas_limit = self.web3_obj.eth.estimateGas(base_trans)
        base_trans['gas'] = gas_limit
        base_trans.pop('from',0)

        signed = w3.eth.account.signTransaction(base_trans, self.priv_key)
        ret = self.web3_obj.eth.sendRawTransaction(signed.rawTransaction)
        print('\t\t https://etherscan.io/tx/%s' % w3.toHex(ret))
