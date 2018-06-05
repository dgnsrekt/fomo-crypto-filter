from exchange_base import BittrexDataFrameCreator, BinanceDataFrameCreator

bittrex = BittrexDataFrameCreator.prepare_dataframes()['BTC']
print('Should be the top % Change on bittrex.')
print(bittrex.sort_values('percent_change').tail(1))  # should equal top %change on website
print()
print('Should be the top Volume on bittrex.')
print(bittrex.sort_values('volume').tail(1))  # should equal top volume on website


from exchange_base import BinanceDataFrameCreator

binance = BinanceDataFrameCreator.prepare_dataframes()['BTC']

print('Should be the top % Change on binance.')
print(binance.sort_values('percent_change').tail(1))  # should equal top %change on website
print()
print('Should be the top volume on binance.')
print(binance.sort_values('volume').tail(1))  # should equal top %change on website

print('Arrows should be down when select a section on the website.')
