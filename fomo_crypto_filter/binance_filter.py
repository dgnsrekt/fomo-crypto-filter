from time import sleep

from exchange import ExchangeDatabase
from structlog import get_logger as logger

# Avaliable Binance Attributes
# 'symbol', 'priceChange', 'priceChangePercent','weightedAvgPrice', 'prevClosePrice',
# 'lastPrice','lastQty', 'bidPrice', 'bidQty', 'askPrice','askQty', 'openPrice',
# 'highPrice', 'lowPrice','volume', 'quoteVolume', 'openTime', 'closeTime',
# 'firstId', 'lastId', 'count', 'baseCurrency'


class BinanceFilter:
    NAME = 'binance'
    COLUMNS = ['quoteVolume', 'priceChangePercent', 'lastPrice']
    INDEX = 'symbol'

    MIN_SIZE = 2
    MAX_SIZE = 6

    def __init__(self, currency_pair):
        self.currency_pair = currency_pair

        self.exchange_data = ExchangeDatabase(BinanceFilter.NAME,
                                              BinanceFilter.COLUMNS,
                                              BinanceFilter.INDEX)

        self.dataframe = self.exchange_data.dataframes[self.currency_pair]

        self.volume_average = self.dataframe['quoteVolume'].mean()
        self.percent_average = self.dataframe['priceChangePercent'].abs().mean()
        self.volume_stdev = self.dataframe['quoteVolume'].std()
        self.percent_stdev = self.dataframe['priceChangePercent'].std()

        self.thresholds = dict()
        self.multipliers = dict()

    def set_multipliers(self, **kwargs):
        for key in kwargs:
            self.multipliers[key] = float(kwargs.get(key))

    def set_thresholds(self):
        if 'volume' in self.multipliers:
            self.thresholds['volume'] = self.volume_average / self.multipliers['volume']
        if 'percent' in self.multipliers:
            self.thresholds['percent'] = self.percent_average / self.multipliers['percent']

        if 'volume_score' in self.multipliers:
            self.thresholds['volume_score'] = round(
                self.volume_stdev + self.volume_average, int(self.multipliers['volume_score']))

        if 'percent_score' in self.multipliers:
            self.thresholds['percent'] = round(
                self.percent_stdev + self.percent_average, int(self.multipliers['percent_score']))

    def filter_dataframe(self):
        df = self.dataframe
        df.columns = ['volume', 'percent', 'price']

        df.sort_values(['percent'], ascending=False, inplace=True)
        for threshold in self.thresholds:
            df = df[df[threshold] > self.thresholds[threshold]]

        # filtered = self.dataframe[self.dataframe['quoteVolume'] > volume_threshold]
        # filtered = filtered[filtered['priceChangePercent'] > percent_threshold]

        # volume_threshold = dataframe['quoteVolume'].mean() * self.multiplier['volume']
        # percent_threshold = dataframe['priceChangePercent'].abs(
        # ).mean() * self.multiplier['percent']

        self.dataframe = df

    def __len__(self):
        return len(self.dataframe)

    def __repr__(self):
        info = f'==== Binance ====\n'
        info += f'Market Average {self.volume_average}\n'
        info += f'Percent Average {self.percent_average}\n'
        info += f'Multipliers: {self.multipliers}\n'
        info += f'Thresholds: {self.thresholds}\n'
        return info


GLOBAL_VOLUME_MULTIPLIER = 0.50
GLOBAL_PERCENT_MULTIPLIER = 32
GLOBAL_VOLUME_SCORE_MULTIPLIER = 1
GLOBAL_PERCENT_SCORE_MULTIPLIER = 4

LAST_PUMPED = []

while True:

    binance_btc_filter = BinanceFilter('BTC')
    binance_btc_filter.set_multipliers(volume=GLOBAL_VOLUME_MULTIPLIER)
    # binance_btc_filter.set_multipliers(percent=GLOBAL_PERCENT_MULTIPLIER)
    # binance_btc_filter.set_multipliers(percent_score=GLOBAL_PERCENT_SCORE_MULTIPLIER)

    binance_btc_filter.set_thresholds()
    binance_btc_filter.filter_dataframe()
    print()
    print(binance_btc_filter)
    print(binance_btc_filter.dataframe)
    print()

    if len(binance_btc_filter) < 2:
        print('list < 2')
        print('reducing volume multiplier.')
        GLOBAL_VOLUME_MULTIPLIER /= 0.5
        # GLOBAL_PERCENT_SCORE_MULTIPLIER /= 0.5

    if len(binance_btc_filter) > 6:
        print('list > 6')
        print('increasing volume multiplier.')
        GLOBAL_VOLUME_MULTIPLIER *= 0.5
        # GLOBAL_PERCENT_SCORE_MULTIPLIER *= 0.5

    sleep(31)


# print(len(binance_btc_filter))
# binance_btc_filter.set_multipliers(volume=.15)
# binance_btc_filter.set_multipliers(percent=32)
# binance_btc_filter.set_thresholds()
# binance_btc_filter.filter_dataframe()
# print(binance_btc_filter)
# print(len(binance_btc_filter))
# print(binance_btc_filter.dataframe)
