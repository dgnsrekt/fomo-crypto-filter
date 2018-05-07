from exchange_base import BinanceDataFrameCreator, BittrexDataFrameCreator
import pickle

in_data = BittrexDataFrameCreator.prepare_dataframes()
# in_data = BinanceDataFrameCreator.prepare_dataframes()
with open('test.pickle', 'wb') as _file:
    pickle.dump(in_data, _file, protocol=pickle.HIGHEST_PROTOCOL)

with open('test.pickle', 'rb') as _file:
    out_data = pickle.load(_file)

btc = out_data['BTC']
print(btc)


class Volume_Dataframe:
    def __init__(self, dataframe):
        self.dataframe = dataframe['volume']

    def update_threshold(self, volume_threshold):
        self.dataframe = self.dataframe[self.dataframe > volume_threshold]

    def return_dataframe(self):
        return self.dataframe

    def __len__(self):
        return len(self.dataframe)

    def __repr__(self):
        rep = f'len: {self.__len__()}\n'
        return rep


class Price_Dataframe:
    def __init__(self, dataframe):
        self.dataframe = dataframe['percent_change']

    def update_threshold(self, price_threshold):
        self.dataframe = self.dataframe[self.dataframe > price_threshold]

    def return_dataframe(self):
        return self.dataframe

    def __len__(self):
        return len(self.dataframe)

    def __repr__(self):
        rep = f'len: {self.__len__()}\n'
        return rep


def rvoFilter(dataframe, initial_weight, gain, target_min, target_max):
    # raw volume filter
    volume_data = dataframe
    weight = initial_weight
    mean = volume_data.volume.mean()

    threshold = mean * weight
    volume_obj = Volume_Dataframe(volume_data)

    volume_obj.update_threshold(threshold)
    steps_taken = 0

    while True:
        if len(volume_obj) > target_max:
            # keep track of runs
            # add logging most of this is debugging
            print('greater than max target')
            print('increasing threshold')
            print(f'weight: {weight}')
            weight += gain
            threshold = mean * weight
            volume_obj.update_threshold(threshold)
            print(volume_obj)
            steps_taken += 1
            if steps_taken > 1000:
                raise Exception('Volume Filter > 1000 steps')
        else:
            print('max target hit')
            break

    while True:
        if len(volume_obj) < target_min:
            print('less than min target')
            print('decreasing threshold')
            print(f'weight: {weight}')
            weight -= gain
            threshold = mean * weight
            volume_obj.update_threshold(threshold)
            print(volume_obj)
            steps_taken += 1
            if steps_taken > 1000:
                raise Exception('Volume Filter > 1000 steps')
        else:
            print('min target hit')
            break

    print(initial_weight)
    print(weight)
    print(steps_taken)
    return volume_obj.return_dataframe()


def rpcFilter(dataframe, initial_weight, gain, target_min, target_max):
    # raw volume filter
    price_data = dataframe
    weight = initial_weight
    mean = price_data.percent_change.mean()

    threshold = mean * weight
    price_obj = Price_Dataframe(price_data)

    price_obj.update_threshold(threshold)
    steps_taken = 0

    while True:
        if len(price_obj) > target_max:
            # keep track of runs
            # add logging most of this is debugging
            print('greater than max target')
            print('increasing threshold')
            print(f'weight: {weight}')
            print(f'threshold: {threshold}')
            weight -= gain
            threshold = mean * weight
            price_obj.update_threshold(threshold)
            print(price_obj)
            steps_taken += 1
            if steps_taken > 1000:
                raise Exception('Volume Filter > 1000 steps')
        else:
            print('max target hit')
            break

    while True:
        if len(price_obj) < target_min:
            print('less than min target')
            print('decreasing threshold')
            print(f'weight: {weight}')
            weight += gain
            threshold = mean * weight
            price_obj.update_threshold(threshold)
            print(price_obj)
            steps_taken += 1
            if steps_taken > 1000:
                raise Exception('Volume Filter > 1000 steps')
        else:
            print('min target hit')
            break

    print(initial_weight)
    print(weight)
    print(steps_taken)
    return price_obj.return_dataframe()


def get_ish(target):
    for max_ in range(5, 50):
        x = rvoFilter(btc, 1, 0.01, 2, max_)
        y = rpcFilter(btc, 1, 0.01, 2, max_)
        x = set(x.index)
        y = set(y.index)

        if len(x.intersection(y)) > (target - 1):
            print(x.intersection(y))
            print(len(x.intersection(y)))
            break
    else:
        print('nothing found')

    print('done')


get_ish(6)
