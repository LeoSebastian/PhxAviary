import configparser
import datetime as dt
import time

from phx_wallet import PhxWallet

class PhxAviary(object):

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('aviary.cfg')
        self.minutes = int(config['global']['frequency'])
        self.frequency = self.minutes * 60 # converts config minutes to seconds
        self.mine_only = config['global']['mine_only']
        self.min_withdraw = float(config['global']['minimum_withdraw'])
        self.min_reinvest = float(config['global']['minimum_reinvest'])
        self.min_bal = float(config['global']['minimum_balance'])
        self.provider = config['global']['provider']
        self.wallets = {}

        for section in config.sections():
            if not (section == 'global'):
                self.wallets[section] = PhxWallet(config[section]['priv_key'],
                    config[section]['pub_key'], self.provider, self.min_withdraw, self.min_reinvest)

    def main(self):
        print('\n\nWelcome to the Aviary v0.1: courtesy of Mr Fahrenheit and Norsefire!')
        print('\nYour global configuration parameters are:')
        print('  Cycle interval (in minutes): \t\t%d' % self.minutes)
        print('  Mainnet INFURA Provider \t\t%s' % self.provider)
        print('  Minimum withdrawal balance: \t\t%f' % self.min_withdraw)
        print('  Minimum reinvest balance: \t\t%f' % self.min_reinvest)
        print('  Minimum account Ether balance: \t%f' % self.min_bal)
        print('  Alter these values in ./aviary.cfg should you choose.')
        while True: # constant loop - gotta love them basic CS principles!
            for key,account in self.wallets.items():
                print ('\n\tInitiating Aviary loop for %s' % account.pub_key)
                print ('\n\t\tCurrent time is %s' % str(dt.datetime.now()))
                print ('\n\t\tChecking if you are eligible to mine PHX: %s' % str(account.mining_dt))
                if dt.datetime.now() >= account.mining_dt:
                    print('Mining now possible. Initiating mine...\n')
                    account.mine()
                else:
                    print ('\t\tMining window not yet elapsed. Continuing on...\n')
                # If your dividend balance has reached over a certain number (i.e. in
                # the event of a heavy dump), withdraw the dividends immediately.
                onlyMine = self.mine_only == "0"
                if (onlyMine):
                    print ('\t\tDetermining if withdrawals or reinvestments are necessary...')
                    if (account.div_bal >= self.min_withdraw):
                        print ('\t\tMinimum withdrawal threshold reached (%s): withdrawing dividends...' % str(account.div_bal))
                        account.withdraw_divs()
                        account.update_div_bal()

                    # Assume that reinvestment will take place, and decide otherwise
                    # if you do not have sufficient gas in your account. If so, it will
                    # withdraw your dividends thus far.
                    else: 
                        reinvest = True
                        if (account.eth_bal < self.min_bal):
                            print ('\t\tAmount of Ether in wallet is lower than your specified minimum. Withdrawing dividends.')
                            account.withdraw_divs()
                            account.update_eth_bal()
                            reinvest = False
                        
                        if reinvest:
                            account.reinvest_divs()
                            account.update_div_bal()
                else:
                    print ('\t\tNon-mining functionality disabled in configuration. Skipping...')
            print ('\n\tCycle complete: entering idle state...\n')
            time.sleep(self.frequency)

phx_aviary = PhxAviary()
phx_aviary.main()
