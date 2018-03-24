import configparser
import datetime as dt
import time,os,sys
from copy import deepcopy

from phx_wallet import PhxWallet

class PhxAviary(object):

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('LIVE_AVIARY.cfg')
        self.frequency = int(config['global']['frequency']) * 60 # convert minutes to seconds
        config_args = {
            'minWithdraw': float(config['global']['minimum_withdraw']),
            'minBuy': float(config['global']['minimum_buy']),
            'minBalance': float(config['global']['minimum_balance']),
            'provider': config['global']['provider']
        }
        self.wallets = {}
        if not(os.path.exists(os.path.join(os.getcwd(), 'logs'))):
            os.makedirs(os.path.join(os.getcwd(), 'logs'))

        for section in config.sections():
            if not (section == 'global'):
                wallet_conf = deepcopy(config_args)
                wallet_conf['id'] = section
                wallet_conf['priv_key'] = config[section]['priv_key']
                wallet_conf['pub_key'] = config[section]['pub_key']
                wallet_conf['mine_only'] = config[section]['mine_only']
                self.wallets[section] = PhxWallet(wallet_conf)

    def mainloop(self):
        # print messages go here ...
        # or in the wallet perhaps
        # figure out how to clear buffer for pretty output
        testing_counter = 0
        while True:
            testing_counter += 1
            if (testing_counter == 2):
                sys.exit()

            for id,wallet in self.wallets.items():
                wallet.update()
                wallet.execute_actions()
            time.sleep(self.frequency)

phx_aviary = PhxAviary()
phx_aviary.mainloop()
