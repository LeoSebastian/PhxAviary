import configparser
import datetime as dt
import time

from phx_wallet import PhxWallet

class PhxAviary(object):

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('aviary.cfg')
        self.frequency = int(config['aviary']['frequency']) * 60 # convert to seconds
        self.min_reinvest = float(config['aviary']['miniumum_reinvest'])
        self.min_bal = float(config['aviary']['minimum_balance'])
        self.provider = config['aviary']['provider']
        self.wallets = {}

        for section in config.sections():
            if not (section == 'aviary'):
                self.wallets[section] = PhxWallet(config[section]['priv_key'],
                    config[section]['pub_key'], self.provider, self.min_reinvest)

    def main(self):
        while True:
            for key,wally in self.wallets.items():
                reinvest = True
                if (wally.eth_bal < self.min_bal):
                    wally.withdraw_divs()
                    wally.update_eth_bal()
                    reinvest = False

                if (dt.datetime.now() >= wally.mining_dt):
                    wally.mine()

                if (reinvest):
                    wally.reinvest_divs()

            time.sleep(self.frequency)

phx_aviary = PhxAviary()
phx_aviary.main()
