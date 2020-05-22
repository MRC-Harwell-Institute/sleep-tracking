#! /usr/bin/env python3

import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from os.path import join
import os
import numpy as np
sns.set(style="white")
sns.set_context("poster")


def _plot_sleep(df, name, outdir):
    fig, ax1 = plt.subplots()
    # Plot 1 month of data, showing activity, dark period of each day and periods of immobility scored as sleep (downward deflection)

    ax1.fill_between(df.index, 0, df['activity'], label="Activty", lw=0, facecolor='#002147')  # activity
    ax1.fill_between(df.index, np.min(df.sleep), np.max(df.activity), where=df.LDR > 100, lw=0, alpha=0.2,
                      facecolor='#aaaaaa')
    ax1.fill_between(df.index, 0, df['sleep'], label="Immobility >40sec", lw=0, facecolor="#030303")
    ax1.set_yticks([])
    ax1.set_xticklabels([])
    ax1.set_frame_on(0)
    figoutdir = join(outdir, 'sleep_figures')
    if not os.path.exists(figoutdir):
        os.mkdir(figoutdir)
    outpath = join(figoutdir, name + '_.png')
    fig.savefig(outpath)


def _sleep_count(val):
    if val == 0:
        _sleep_count.count = 0
    elif val == 1:
        _sleep_count.count += 1
    return _sleep_count.count

_sleep_count.count = 0  # static variable. TODO: what is this doing here?


def cum_sleep_bouts_fig(config):

    def sleepscan(a):
        bins = int(config.sleep_period / config.original_bin_size)
        ss = a.rolling(bins).sum()
        y = ss == 0
        return y.astype(int)  # if numerical output is required

    df = config.df

    # identify the 40s sleep bouts at each 10s timestamp if there has bee >=4 zero values,
    # add a 1 in the activity column
    df[config.columns_to_use].apply(sleepscan)

    df_sleep = pd.DataFrame(df[config.columns_to_use].apply(sleepscan))

    df_cum_sleep = df_sleep.applymap(_sleep_count)

    for detector in config.columns_to_use:
        sleep = 0 - (df_cum_sleep[detector] / df_cum_sleep[detector].max())

        activity = (df[detector] / df[detector].max())

        # TODO: What is no LDR column?
        new_df = pd.DataFrame.from_dict({'activity': activity, 'sleep': sleep, 'LDR': df.LDR})

        _plot_sleep(new_df, detector, config.outdir)


if __name__ == '__main__':
    import cfg_load
    cum_sleep_bouts_fig(cfg_load.load_config(sys.argv[1]))