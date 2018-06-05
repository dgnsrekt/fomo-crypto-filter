from exchange_base import BinanceDataFrameCreator, BittrexDataFrameCreator
from filters import super_filter
from pumplist import PumpingList
import logging

logging.basicConfig(level='INFO')


from time import sleep
from sound import play
# import multiprocessing
import threading
import schedule

binance_pumplist = PumpingList('Binance')
bittrex_pumplist = PumpingList('Bittrex')

# TODO: ADD retry


def binance():
    while True:
        # schedule.run_pending() # add schedule for clearing list every x time.
        binance_data = BinanceDataFrameCreator.prepare_dataframes()
        data = binance_data['BTC']

        binance_watchlist = super_filter(data)  # <<< reuse
        for coin in binance_watchlist:
            binance_pumplist.update(coin)
            if binance_pumplist.pumping:
                play()
                print(f'{binance_pumplist.pumping} is pumping on {binance_pumplist.name}')  # <<< reuse
                # need to add a url to click on
        # print('Binance')
        sleep(30)
        # print('sleeping 30s...')


def bittrex():
    while True:
        bittrex_data = BittrexDataFrameCreator.prepare_dataframes()
        data = bittrex_data['BTC']
        bittrex_watchlist = super_filter(data)
        for coin in bittrex_watchlist:
            bittrex_pumplist.update(coin)
            if bittrex_pumplist.pumping:
                play()
                print(f'{bittrex_pumplist.pumping} is pumping on {bittrex_pumplist.name}')
                # need to add a url to click on

        # print('Bittrex')
        sleep(60)
        # print('sleeping 60s...')


def clear_list():
    PumpingList.previously_pumped.clear()  # try 4, 6 12 hour next
    x = '#' * 20
    print(f'{x}list cleared{x}')


def summary():
    schedule.every().day.do(clear_list)
    while True:
        schedule.run_pending()  # add schedule for clearing list every x time.
        sleep(300)
        print('summary')
        print(PumpingList.previously_pumped)


tid1 = threading.Thread(target=binance)
tid2 = threading.Thread(target=bittrex)
tid3 = threading.Thread(target=summary)

tid1.start()
tid2.start()
tid3.start()

tid1.join()
tid2.join()
tid3.join()
# proc1 = multiprocessing.Process(target=binance)
# proc2 = multiprocessing.Process(target=bittrex)

# proc1.start()
# proc2.start()

# proc1.join()
# proc2.join()
