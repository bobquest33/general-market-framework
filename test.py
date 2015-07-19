# -*- coding: utf-8 -*-

from ethereum import tester, slogging, utils
import os

state = tester.state()

# Create Market Contract
# TODO: remove gas
market = state.abi_contract('contracts/market.se', gas=10000000)


# Create Match Maker
class Matchmaker:

    def new_block(self, block):
        print('new block', block)

    def announce(self, data):
        ''' A new ticket has arrived '''
        ticket = data[0]
        info = market.get_info(ticket)
        preferences = market.get_preferences(ticket)
        print('ticket #', ticket)
        print('ticket info', info)
        print('ticket preferences', preferences)

    def listener(self, msg):
        '''
        Dynamically call Methods based on first param
        Currently only announce exists

        Also iterates on blocks
        '''
        event = msg['event']
        if event == 'LOG' and msg['to'] == self.market:
            msg_type = utils.encode_int(msg['topics'][0]).rstrip('\x00')
            msg_data = msg['topics'][1:]
            try:
                getattr(self, msg_type)(msg_data)
            except:
                raise NotImplementedError(msg_type, msg_data)
        elif event == 'delta':
            if self.current_block < state.block.number:
                self.current_block = state.block.number
                self.new_block(state.block.number)

    def __init__(self, market):
        self.market = market
        self.current_block = -1
        slogging.log_listeners.listeners.append(self.listener)

# TODO: Confirm this is correct?
market_addr = '\xc3\x05\xc9\x01\x07\x87\x81\xc22\xa2\xa5!\xc2\xafy\x80\xf88^\xe9'
match_maker = Matchmaker(market_addr)

state.mine(n=1)

# Create buy ticket, add preferences, activate
buy_ticket = market.add()
market.add_preference(buy_ticket, 'head', 10)
market.add_preference(buy_ticket, 'tail', 20)
market.add_preference(buy_ticket, 'price', 5)
market.activate(buy_ticket)

# Create sell ticket, add preferences, activate
sell_ticket = market.add()
market.add_preference(sell_ticket, 'price', -5)
market.activate(sell_ticket)

# print('reveal', market.add_sealed_offer(0, 1))
