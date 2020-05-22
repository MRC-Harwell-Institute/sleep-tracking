#!/usr/bin/env python3

"""
sleep_counting.py

TODO: The plots are not saving correclty when this script is run as an importted module, but works when run directly
from the command line


"""

import sys
import toml
from addict import Dict
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from os.path import join


def sleep_counting(config):

    def _sleepscan(a):
        # For each time stamp return whether the mouse was asleep (1) or not (0)
        # For mouse to be classed asleep it must have been inactive for at least 'sleep_period' seconds
        bins = int(sleep_period / original_bin_size)
        ss = a.rolling(bins).sum()
        y = ss == 0
        return y.astype(int)

    sns.set(style="white")
    sns.set_context("poster")

    bin_size_mins = config.sleep_counting_bin_size_mins

    sleep_period = config.sleep_period # The minimum time of inactivity to call sleeping
    original_bin_size = config.original_bin_size

    columns_to_use = config.columns_to_use

    df = config.df

    # identify the 40s sleep bouts at each 10s timestam if there has bee >=4 zero values,
    # add a 1 in the activity column
    df[columns_to_use].apply(_sleepscan)

    df_sleep = pd.DataFrame(df[columns_to_use].apply(_sleepscan))

    # Reasmaple to binsize
    # Count all the time points in theat bin that are part of a sleep bout
    # Convert to total seconds asleep in each bin
    df_sleep_bin = df_sleep.resample('{}T'.format(bin_size_mins)).sum() * original_bin_size

    axes = df_sleep_bin.plot(kind='bar', subplots=True, legend=False)

    for ax in axes:
        ax.get_yaxis().set_visible(False)

    df_sleep_bin.plot.bar(subplots=True, legend=False)

    plt.tight_layout()

    plt_path = join(config.outdir, 'total_sleep_secs_in_{}_min_bins.png'.format(bin_size_mins))
    plt.savefig(plt_path)

    csv_path = join(config.outdir, 'total_sleep_secs_in_{}_min_bins.csv'.format(bin_size_mins))
    df_sleep_bin.to_csv(csv_path)


if __name__ == '__main__':
    import cfg_load
    sleep_counting(cfg_load.load_config(sys.argv[1]))