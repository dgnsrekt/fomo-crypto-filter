
class DataFrameFilter:

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


class BaseFilter:

    def __init__(self, dataframe, filter_column, initial_weight=1, initial_gain=0.1):
        # may remove targets may call on methond
        self.weight = initial_weight
        self.gain = initial_gain
        self.steps_taken = 0
        self.bias = self._set_bias(filter_column, dataframe)
        # print('using', self.__class__.__name__, self.bias)
        self.threshold = self.bias * self.weight
        # need private method to create filtered_data for positive only filter
        self.data = self._prep_data(dataframe, filter_column)
        self.data.update_threshold(self.threshold)

    def _set_bias(self, filter_column, dataframe):
        return dataframe[filter_column].mean()
        # override this method to create other types of filters

    def _prep_data(self, dataframe, filter_column):
        return DataFrameFilter(dataframe, filter_column)
        # override for pre filtering input data

    def filter_data(self, target_min=1, target_max=8):
        while True:
            if len(self.data) > target_max:
                self._increase_threshold()
                if self.steps_taken > 10000:
                    break
            else:
                # print('Max target hit')
                break

        while True:
            if len(self.data) < target_min:
                self._decrease_threshold()

                if self.steps_taken > 10000:
                    break
                if self.threshold <= 0:
                    break
            else:
                # print('Min Target hit')
                break

        return self.data.return_dataframe()

    def _increase_threshold(self):
        # print(self.data)
        self.weight += self.gain
        self.threshold = self.bias * self.weight
        self.data.update_threshold(self.threshold)
        self.steps_taken += 1
        # print('increased')
        # print(self)  # add to debug with sleep

    def _decrease_threshold(self):
        # print(self.data)
        self.weight -= self.gain
        self.threshold = self.bias * self.weight
        self.data.update_threshold(self.threshold)
        self.steps_taken += 1
        # print('decreased')
        # print(self)

    def __repr__(self):
        _repr = f'weight: {self.weight}\n'
        _repr += f'threshold: {self.threshold}\n'
        _repr += f'steps taken: {self.steps_taken}\n'
        return _repr


class AbsoluteMeanFilter(BaseFilter):
    def __init__(self, dataframe, filter_column, initial_weight=1, initial_gain=0.1):
        BaseFilter.__init__(self, dataframe, filter_column, initial_weight, initial_gain)
        pass

    def _set_bias(self, filter_column, dataframe):
        return dataframe[filter_column].abs().mean()


class AbsoluteMedianFilter(BaseFilter):
    def __init__(self, dataframe, filter_column, initial_weight=1, initial_gain=0.1):
        BaseFilter.__init__(self, dataframe, filter_column, initial_weight, initial_gain)
        pass

    def _set_bias(self, filter_column, dataframe):
        return dataframe[filter_column].abs().median()


class PositiveMeanFilter(BaseFilter):
    def __init__(self, dataframe, filter_column, initial_weight=1, initial_gain=0.01):
        BaseFilter.__init__(self, dataframe, filter_column, initial_weight, initial_gain)
        pass

    def _set_bias(self, filter_column, dataframe):
        df = dataframe[dataframe[filter_column] > 0]
        return df[filter_column].mean()  # shouldnt need absolute should be positve already

    def _prep_data(self, dataframe, filter_column):
        df = dataframe[dataframe[filter_column] > 0]

        return DataFrameFilter(df, filter_column)


class PositiveMedianFilter(BaseFilter):
    def __init__(self, dataframe, filter_column, initial_weight=1, initial_gain=0.01):
        BaseFilter.__init__(self, dataframe, filter_column, initial_weight, initial_gain)
        pass

    def _set_bias(self, filter_column, dataframe):
        df = dataframe[dataframe[filter_column] > 0]
        return df[filter_column].median()  # shouldnt need absolute should be positve already

    def _prep_data(self, dataframe, filter_column):
        df = dataframe[dataframe[filter_column] > 0]

        return DataFrameFilter(df, filter_column)


def super_filter(_data, _target_iterations=50, max_results=3):
    for _max in range(2, _target_iterations + 1):

        data = _data
        afilter_pct = AbsoluteMedianFilter(data, 'percent_change')
        aset_pct = afilter_pct.filter_data(target_max=_max)

        afilter_vol = AbsoluteMedianFilter(data, 'volume')
        aset_vol = afilter_vol.filter_data(target_max=_max)

        bfilter_pct = AbsoluteMeanFilter(data, 'percent_change')
        bset_pct = bfilter_pct.filter_data(target_max=_max)

        bfilter_vol = AbsoluteMeanFilter(data, 'volume')
        bset_vol = bfilter_vol.filter_data(target_max=_max)

        cfilter_pct = PositiveMeanFilter(data, 'percent_change')
        cset_pct = cfilter_pct.filter_data(target_max=_max)

        cfilter_vol = PositiveMeanFilter(data, 'volume')
        cset_vol = cfilter_vol.filter_data(target_max=_max)

        dfilter_pct = PositiveMedianFilter(data, 'percent_change')
        dset_pct = dfilter_pct.filter_data(target_max=_max)

        dfilter_vol = PositiveMedianFilter(data, 'volume')
        dset_vol = dfilter_vol.filter_data(target_max=_max)

        aset_pct = set(aset_pct.index)
        aset_vol = set(aset_vol.index)

        bset_pct = set(bset_pct.index)
        bset_vol = set(bset_vol.index)

        cset_pct = set(cset_pct.index)
        cset_vol = set(cset_vol.index)

        dset_pct = set(dset_pct.index)
        dset_vol = set(dset_vol.index)

        results = aset_pct.intersection(
            aset_vol, bset_pct, bset_vol)
        # results = aset_pct.intersection(
        # aset_vol, bset_pct, bset_vol, cset_pct, cset_vol, dset_pct, dset_vol)
        # print('Current', results, 'Current Filter Step:', _max)
        if len(results) >= max_results:
            # print(results)
            # print('Breaking Loop')
            return results
            break

    else:
        print('Loop Complete')
        print(results)
        return results


#
# bfilter = AbsoluteMeanFilter(data, 'percent_change')
# bfiltered = bfilter.filter_data()
# bsteps = bfilter.steps_taken
#
# cfilter = PositiveMeanFilter(data, 'percent_change')
# cfiltered = cfilter.filter_data()
# csteps = cfilter.steps_taken
#
# dfilter = PositiveMedianFilter(data, 'percent_change')
# dfiltered = dfilter.filter_data()
# dsteps = dfilter.steps_taken

# print(afiltered)
# print(asteps)
# print(bfiltered)
# print(bsteps)
# print(cfiltered)
# print(csteps)
# print(dfiltered)
# print(teps)
