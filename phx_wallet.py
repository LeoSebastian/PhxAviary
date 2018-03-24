import datetime as dt
import time,sys,csv,os

import phx_abi
custom_abi = phx_abi.get_abi()

from web3 import HTTPProvider, Web3
from web3.auto import w3

class PhxWallet(object):

    def __init__(self, args):
        self.id = args['id']
        self.priv_key = args['priv_key']
        self.pub_key = args['pub_key']
        self.conf = args
        self.web3_obj = Web3(HTTPProvider(args['provider']))
        self.ethphoenix   = self.web3_obj.eth.contract(address='0x2Fa0ac498D01632f959D3C18E38f4390B005e200', abi=custom_abi)
        self.phoenixcoin  = self.web3_obj.eth.contract(address='0x14b759A158879B133710f4059d32565b4a66140C', abi=custom_abi)
        self.datalog_path = os.path.join(os.getcwd(), 'logs', '%s_data.csv' % self.id)
        self.actionlog_path = os.path.join(os.getcwd(), 'logs', '%s_transactions.csv' % self.id)
        ### check that the wallet has EPX
        epx_bal = self.ethphoenix.functions.tokenBalance(self.pub_key).call()
        if (epx_bal == 0):
            sys.exit('ERROR: This wallet has no EPX: %s' % self.pub_key)

        ##### Initial variables
        self.data = {
            'dt': None,                 ## Current timestamp
            'miningCooldown': None,     ## Countdown to mine
            'walletBalance': 0.0,       ## ETH balance of wallet
            'epx': 0.0,                 ## EPX baLance in contract
            'phx': 0.0,                 ## PHX balance in wallet
            'dividends': 0.0,           ## Dividends in contract
            'buyPrice': 0.0,            ## Buy price of tokens
            'sellPrice': 0.0,           ## Sell price of tokens
            'epxAction': None,          ## EPX action for given iteration
            'phxAction': None           ## PHX action for given iteration
        }

    def update(self):
        self.data['dt'] = dt.datetime.now().strftime('%c')
        self.data['miningCooldown'] = self.phoenixcoin.functions.miningCooldown().call({'from': self.pub_key})
        self.data['walletBalance'] = self.web3_obj.fromWei(self.web3_obj.eth.getBalance(self.pub_key), 'ether')
        self.data['epx'] = self.web3_obj.fromWei(self.ethphoenix.functions.tokenBalance(self.pub_key).call(), 'ether')
        self.data['phx'] = self.web3_obj.fromWei(self.phoenixcoin.functions.balanceOf(self.pub_key).call(), 'ether')
        self.data['dividends'] = self.web3_obj.fromWei(self.ethphoenix.functions.dividends(self.pub_key).call(), 'ether')
        self.data['buyPrice'] = self.web3_obj.fromWei(self.ethphoenix.functions.buyPrice().call(), 'ether')
        self.data['sellPrice'] = self.web3_obj.fromWei(self.ethphoenix.functions.sellPrice().call(), 'ether')
        self.update_actions()

        data_headers = ['dt', 'miningCooldown', 'walletBalance', 'epx', 'phx', 'dividends',
            'buyPrice', 'sellPrice', 'phxAction', 'epxAction']
        if not (os.path.isfile(self.datalog_path)):
            with open(self.datalog_path, 'w', newline='') as new:
                writer = csv.writer(new)
                writer.writerow(data_headers)

        outrow = []
        [outrow.append(self.data[x]) for x in data_headers]
        with open(self.datalog_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(outrow)

    def update_actions(self):
        self.data['phxAction'] = 'wait'
        if (self.data['miningCooldown'] == 0):
            self.data['phxAction'] = 'mine'

        if (self.data['walletBalance'] < self.conf['minBalance']):
            print('Minimum balance: %f' % self.conf['minBalance'])
            if (self.data['dividends'] + self.data['walletBalance'] > self.conf['minBalance']):
                self.data['epxAction'] = 'withdraw:insuffientFunds'
            else:
                self.data['epxAction'] = 'wait:insufficientFunds'
                self.data['phxAction'] = 'wait:insufficientFunds'
        else:
            self.data['epxAction'] = 'wait:noThresholdsReached'         # pre-set
            if (self.data['dividends'] > self.conf['minBuy']):
                self.data['epxAction'] = 'buy:thresholdReached'
            if (self.data['dividends'] > self.conf['minWithdraw']):     # withdraw takes priority
                self.data['epxAction'] = 'withdraw:thresholdReached'    # thus it is checked second

    def execute_actions(self):
        if (self.data['phxAction'] == 'mine'):
            self.raw_txn('0x14b759A158879B133710f4059d32565b4a66140C','0x99f4b251', 'mine')

        epx_action = self.data['epxAction'].split(':')[0]
        if (epx_action == 'buy'):
            self.raw_txn('0x2Fa0ac498D01632f959D3C18E38f4390B005e200','0x957b2e56',self.data['epxAction'])
        elif (epx_action == 'withdraw'):
            self.raw_txn('0x2Fa0ac498D01632f959D3C18E38f4390B005e200','0x3ccfd60b',self.data['epxAction'])

    def raw_txn(self, addr, txn_data, action):
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
        print('https://etherscan.io/tx/%s' % w3.toHex(ret))
        outrow = [dt.datetime.now().strftime('%c'), action, 'https://etherscan.io/tx/%s' % w3.toHex(ret)]
        with open(self.actionlog_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(outrow)
