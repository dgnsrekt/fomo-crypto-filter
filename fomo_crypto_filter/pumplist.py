#!python3.6


class PumpingList:
    previously_pumped = set()

    def __init__(self, name):
        self.name = name
        self.pumping = set()

    @classmethod
    def clear(cls):
        cls.previously_pumped = set()

    def update(self, items):
        self.pumping = set()
        if items:
            items = items.replace(' ', '').replace('-', '').replace('/', '')
            items = f'{self.name.upper()}:{items}'
            last = set([items])  # IDEA: set([(items, name)])
            self.pumping = last.difference(PumpingList.previously_pumped)
            # the difference between the old and the new
            PumpingList.previously_pumped.update(last)

    def __repr__(self):
        repr_ = f'name: {self.name} '
        repr_ += f'previously_pumped: {PumpingList.previously_pumped} '
        repr_ += f'pumping: {self.pumping} '
        return repr_

#
# import random
#
# coins = ['BTC', 'LTC', 'ETH', 'ETC', 'USDT']
#
# binance_pumplist = PumpingList('Binance')
# bittrex_pumplist = PumpingList('Bittrex')
#
# while True:
#     coin = random.choice(coins)
#     binance_pumplist.update(coin)
#
#     coin = random.choice(coins)
#     bittrex_pumplist.update(coin)
#
#     for exchange in [binance_pumplist, bittrex_pumplist]:
#         if exchange.pumping:
#             print(f'{exchange.pumping} is pumping on {exchange.name}')
#
#     break
#
# x = set([1, 2, 3, 4, 5])
# y = set([2, 4, 6])
#
# z = y.difference(x)
# print(z)
# x.update(y)
# print(x)
