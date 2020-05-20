#!/usr/bin/env python

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from os.path import join
from matplotlib.dates import DateFormatter


def sleep_counting(config):

    def _sleepscan(a):
        bins = int(sleep_period / original_bin_size)
        ss = a.rolling(bins).sum()
        y = ss == 0
        return y.astype(int)  # if numerical output is required

    sns.set(style="white")
    sns.set_context("poster")

    bin_size_mins = 30


    data_path = config.data_abs_path
    sleep_period = config.sleep_period
    original_bin_size = config.original_bin_size
    time_start = config.time_start
    time_end = config.time_end

    columns_to_remove = config.columns_to_remove
    columns_to_use = config.columns_to_use

    df = config.df

    # identify the 40s sleep bouts at each 10s timestam if there has bee >=4 zero values,
    # add a 1 in the activity column
    df[columns_to_use].apply(_sleepscan)

    df_sleep = pd.DataFrame(df[columns_to_use].apply(_sleepscan))

    # Sum up all the 10s periods where any of the periods belongs to a >=40s sleep bout and convert to total seconds
    df_sleep_bin = df_sleep.resample('{}T'.format(bin_size_mins)).sum() * 10

    axes = df_sleep_bin.plot(kind='bar', subplots=True, legend=False)
    formatter = DateFormatter('%H:%M')
    for ax in axes:
        # ax.xaxis.set_major_formatter(formatter)
        ax.get_yaxis().set_visible(False)
    plt.tight_layout()


    plt_path = join(config.outdir, 'total_sleep_mins_in_{}_min_bins.png'.format(bin_size_mins))
    plt.savefig(plt_path)

    csv_path = join(config.outdir, 'total_sleep_mins_in_{}_min_bins.csv'.format(bin_size_mins))
    df_sleep_bin.to_csv(csv_path)
    print('finished')


if __name__ == '__main__':
    sleep_counting()