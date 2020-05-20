"""
Settings.py: Put the settings here fo rthe other scripts to use
"""

from pathlib import Path
import pandas as pd
##################################################
# Where to store the output
outdir = Path(r'/home/neil/Desktop/t/sleep_test')

# Path to the data file
data_path = r'/home/neil/git/sleep-tracking/data/PIR_example_data.csv'
# data_path = r'/home/neil/bit/Members/Neil_Horner/labbook_2017/Journal/2018/07/16/180619_1450 coffin 19.csv'

# data_path = r'/home/neil/Desktop/petrina/raw_151019_1137.csv'

# data_path = r'/home/neil/bit/External_work/Gareth/Gareth_PIR/test_data/160616_1423_Circa_13_comma_removed.csv'
# The bin size of the input data
original_bin_size = 5

new_bin_size_mins = 1


# What minimally defines a sleep bout in seconds
sleep_period = 40

time_bin_for_mean_sleep_bout_calculation_mins = 30

# The range of time to analyze. Below is one day example
time_start = pd.to_datetime("2017-03-16 11:00:00").tz_localize('UTC')
time_end = pd.to_datetime("2017-03-23 11:00:00").tz_localize('UTC')


# debugging
# time_start = "2017-02-22 12:43:00"  # lights on -> day 1. 12hr -> day1 lights off
# time_end = "2017-02-24 12:43:00"


# Columns that should not be analysed
columns_to_remove = []  # animals to remove

# columns that should be analysed
columns_to_use = ['PIR1', 'PIR2', 'PIR3', 'PIR4', 'PIR5']

##################################################
# Do not edit below here

import os
from os.path import join, realpath, dirname
import pandas as pd
import os
import tempfile
import sys

# As some of the csv files have trailing commas, remove them and save to temporary file for panbdas reading
import csv


def monotinic_increasing(df):
    # check whether monotonic increaseing and print indices where this occurs
    if not all([x < y for x, y in zip(df.index, df.index[1:])]):
        indices = [i for i, x in enumerate([x < y for x, y in zip(df.index, df.index[1:])]) if not x]
        # Now remove the duplicates
        for idx in indices:
            start_time = df.index[idx]
            for i in range(idx, df.index.size):
                test_time = df.index[i]
                if start_time < test_time:
                    print('#####################################################')
                    print('non monotonic section:')
                    print('start row:', idx)
                    print('end row:', i)
                    print(df[idx - 2: i + 2].index)
                    print('size', df[idx - 2: i + 2].index.size)
                    print('#####################################################')
                    break
        return False
    else:
        return True


script_dir = dirname(realpath(__file__))
data_abs_path = join(script_dir, data_path)

# Make the outdir
if not os.path.exists(outdir):
    os.mkdir(outdir)

# read in the time series data
df = pd.read_csv(data_path)

# Delete the unused columns
df.drop(columns_to_remove, axis=1, inplace=True)

# Convert timestamp to DateTime objects
df = df.set_index(pd.to_datetime(df.Time))
del df['Time']

if not monotinic_increasing(df):
    import sys
    sys.exit()

# Truncate to specified time range
df = df.truncate(before=time_start, after=time_end)
if df.size < 1:
    sys.exit('dataframe has zero size. Is the datetime range correct?')


