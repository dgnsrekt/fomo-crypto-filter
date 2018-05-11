from exchange_base import BinanceDataFrameCreator, BittrexDataFrameCreator
import pickle


class Dirty_Dataframe:

    def __init__(self, dataframe, column):
        self.name = column
        self.dataframe = dataframe[column]

    def update_threshold(self, threshold):
        self.dataframe = self.dataframe[self.dataframe > threshold]

    def return_dataframe(self):
        return self.dataframe

    def __len__(self):
        return len(self.dataframe)

    def __repr__(self):
        _repr = f'len: {self.__len__()}\n'
        return _repr


from time import sleep


def _filter(*, _dataframe, filter_column, initial_weight, gain, target_min, target_max):
    dataframe = _dataframe
    weight = initial_weight
    mean = dataframe[filter_column].abs().mean()
    # mean = dataframe[filter_column].abs().median()

    threshold = mean * weight
    filtered_data = Dirty_Dataframe(dataframe, filter_column)

    filtered_data.update_threshold(threshold)
    steps_taken = 0

    while True:
        if len(filtered_data) > target_max:
            # keep track of runs
            # add logging most of this is debugging
            print('greater than max target')
            print('increasing threshold')
            print(f'weight: {weight}')
            weight += gain
            threshold = mean * weight
            filtered_data.update_threshold(threshold)
            print(str(filtered_data))
            steps_taken += 1
            if steps_taken > 10000:
                raise Exception('Volume Filter > 10000 steps')
        else:
            print('max target hit')
            break

    while True:
        if len(filtered_data) < target_min:
            print('less than min target')
            print('decreasing threshold')
            print(f'weight: {weight}')
            weight -= gain
            threshold = mean * weight
            filtered_data.update_threshold(threshold)
            print(f'threshold: {threshold}')
            print(f'mean: {mean}')
            print(str(filtered_data))
            steps_taken += 1
            if steps_taken > 10000:
                raise Exception('Volume Filter > 10000 steps')

        elif weight <= 0:
            print('weight is less than zero')
            break
        else:
            print('min target hit')
            break

    print(initial_weight)
    print(weight)
    print(steps_taken)
    return filtered_data.return_dataframe()


def filter_best(target, _dataframe, initial_weight=1, gain=0.1, target_min=3):
    # maybe package args into dict then pass *args to filter
    for max_ in range(5, 50):
        x = _filter(_dataframe=_dataframe, filter_column='volume',
                    initial_weight=initial_weight, gain=gain, target_min=target_min, target_max=max_)

        y = _filter(_dataframe=_dataframe, filter_column='percent_change',
                    initial_weight=initial_weight, gain=gain, target_min=target_min, target_max=max_)
        x = set(x.index)
        y = set(y.index)

        if len(x.intersection(y)) > (target - 1):
            print(x.intersection(y))
            print(len(x.intersection(y)))
            break
    else:
        if len(x.intersection(y)) > 1:
            print(x.intersection(y))
            print(len(x.intersection(y)))
        else:
            print('nothing found')

    print('done')


#
#
in_data = BinanceDataFrameCreator.prepare_dataframes()
with open('test.pickle', 'wb') as _file:
    pickle.dump(in_data, _file, protocol=pickle.HIGHEST_PROTOCOL)
#
with open('test.pickle', 'rb') as _file:
    out_data = pickle.load(_file)


#
for x in out_data:
    print(out_data[x])  # these settings wont work across btc, eth, usdt, cant loop
    sleep(2)
    filter_best(8, out_data[x])  # these settings wont work across btc, eth, usdt, cant loop
    print('binance', x)
    sleep(2)

#---------------------------------------------


in_data = BittrexDataFrameCreator.prepare_dataframes()

with open('test.pickle', 'wb') as _file:
    pickle.dump(in_data, _file, protocol=pickle.HIGHEST_PROTOCOL)

with open('test.pickle', 'rb') as _file:
    out_data = pickle.load(_file)

bittrex = out_data['BTC']
print(bittrex['percent_change'].mean())
print(bittrex.describe())

for x in out_data:
    filter_best(3, out_data[x])
    print('bittrex', x)
    sleep(5)
