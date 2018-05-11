import ccxt
import pandas as pd

from ccxt.base.errors import RequestTimeout
from structlog import get_logger as logger


class ExchangeInterface:

    def __init__(self, exchange):
        self._log = logger()

        self.exchange = ExchangeInterface.connect(exchange)
        self.id = self.exchange.id
        self._log.debug('Succesfully initialized.', exchange=self.id)

    @classmethod
    def connect(cls,  exchange):
        return getattr(ccxt, exchange)({'enableRateLimit': True})

    def pull_tickers(self):
        self._log.debug('Fetching tickers', exchange=self.id)
        tickers = self.exchange.fetchTickers()
        return tickers

    @classmethod
    def sort_tickers(cls, unsorted_ticker_data):
        _sorted_tickers = []

        for ticker in unsorted_ticker_data:
            ticker_information = unsorted_ticker_data[ticker]['info']
            ticker_base = ticker.split('/')
            if len(ticker_base) > 1:
                ticker_information['basecurrency'] = ticker_base[1]
            _sorted_tickers.append(ticker_information)
        return _sorted_tickers

    @classmethod
    def get_avaliable_columns_from_exchange(cls, exchange):
        _exchange = getattr(ccxt, exchange)({'enableRateLimit': True})
        _ticker_data = _exchange.fetchTickers()
        _random_ticker = next(iter(_ticker_data.items()))[0]
        print(list(_ticker_data[_random_ticker].keys()))


class BinanceDataFrameCreator:

    @classmethod
    def prepare_dataframes(cls):
        columns = ['quoteVolume', 'priceChangePercent']
        index = 'symbol'

        exchange = ExchangeInterface('binance')

        unsorted_ticker_data = exchange.pull_tickers()
        sorted_ticker_data = exchange.sort_tickers(unsorted_ticker_data)

        dataframe = pd.DataFrame(sorted_ticker_data)

        columns.append(index)
        columns.append('basecurrency')

        dataframe = dataframe[columns].set_index(index)

        columns.remove(index)
        columns.remove('basecurrency')

        base_pairs = [base for base in dataframe['basecurrency'].unique() if isinstance(base, str)]

        output_data = dict()

        for pair in base_pairs:
            output_data[pair] = dataframe[dataframe['basecurrency'] == pair]
            output_data[pair] = output_data[pair][columns].apply(pd.to_numeric, errors='coerce')
            output_data[pair].columns = ['volume', 'percent_change']

        output_data.pop('USDT')  # dump USDT DATA Filter doesnt like it.

        return output_data


class BittrexDataFrameCreator:

    @classmethod
    def prepare_dataframes(cls):
        columns = ['BaseVolume', 'percent_change']
        index = 'MarketName'

        exchange = ExchangeInterface('bittrex')

        unsorted_ticker_data = exchange.pull_tickers()
        sorted_ticker_data = exchange.sort_tickers(unsorted_ticker_data)

        dataframe = pd.DataFrame(sorted_ticker_data)
        # percent change  = old -  new / old * 100
        dataframe['percent_change'] = (
            dataframe['PrevDay'] - dataframe['Last'])/dataframe['PrevDay'] * 100

        columns.append(index)
        columns.append('basecurrency')

        dataframe = dataframe[columns].set_index(index)

        columns.remove(index)
        columns.remove('basecurrency')

        base_pairs = [base for base in dataframe['basecurrency'].unique() if isinstance(base, str)]

        output_data = dict()

        for pair in base_pairs:
            output_data[pair] = dataframe[dataframe['basecurrency'] == pair]
            output_data[pair] = output_data[pair][columns].apply(pd.to_numeric, errors='coerce')
            output_data[pair].columns = ['volume', 'percent_change']

        return output_data


# x = BittrexDataFrameCreator.prepare_dataframes()
# print(x['BTC'].describe())


class PoloniexDataFrameCreator:
    from poloniex import Poloniex
    polo = Poloniex()
    currencies = polo.returnCurrencies()
    currency_key = {}
    for tick in currencies:
        currency_key[currencies[tick]['id']] = tick

    @classmethod
    def prepare_dataframes(cls):
        columns = ['baseVolume', 'percentChange']
        index = 'MarketName'

        exchange = ExchangeInterface('poloniex')

        unsorted_ticker_data = exchange.pull_tickers()
        sorted_ticker_data = exchange.sort_tickers(unsorted_ticker_data)

        dataframe = pd.DataFrame(sorted_ticker_data)
        # dataframe['symbol'] = PoloniexDataFrameCreator.currency_key[dataframe['id']]
        # print(dataframe.head())
        # dataframe['percent_change'] = (
        # dataframe['Last'] - dataframe['PrevDay'])/dataframe['Last'] * 100
        #
        # columns.append(index)
        # columns.append('basecurrency')
        #
        # dataframe = dataframe[columns].set_index(index)
        #
        # columns.remove(index)
        # columns.remove('basecurrency')
        #
        # base_pairs = [base for base in dataframe['basecurrency'].unique() if isinstance(base, str)]
        #
        # output_data = dict()
        #
        # for pair in base_pairs:
        #     output_data[pair] = dataframe[dataframe['basecurrency'] == pair]
        #     output_data[pair] = output_data[pair][columns].apply(pd.to_numeric, errors='coerce')
        #     output_data[pair].columns = ['volume', 'percent_change']
        #
        # return output_data
        #
# bittrex = ExchangeInterface('bittrex')
# x = bittrex.pull_tickers()
# print(x['ETH/BTC']['percentage'])
# print(x['ETH/BTC']['quoteVolume'])


# x = BinanceDataFrameCreator.prepare_dataframes()
# print(x)
# x = BittrexDataFrameCreator.prepare_dataframes()
# print(x)
# x = PoloniexDataFrameCreator.prepare_dataframes()
# print(x)

# binance = ExchangeDatabase(exchange='binance', columns=[
#                            'volume', 'quoteVolume', 'priceChangePercent',
#                            'weightedAvgPrice', 'lastPrice'],
#                            index_column='symbol')
#
# bittrex = ExchangeDatabase(exchange='bittrex', columns=[
#                            'Volume', 'BaseVolume', 'Bid',
#                            'High', 'Low', 'Ask',
#                            'Last'], index_column='MarketName')
# poloniex = ExchangeDatabase(exchange='poloniex', columns=[
#                             'baseVolume', 'quoteVolume', 'percentChange'
#
#                             ], index_column='id')
#
# exchanges = [bittrex, poloniex, binance]
#
# for ex in exchanges:
#     print(f'===={ex.id}====')
#     for base in ['BTC', 'ETH', 'USDT']:
#         print(f'----{base}----')
#         try:
#             print(ex.dataframes.get(base).tail())
#         except AttributeError:
#             pass
