#! /usr/bin/env python3

import pandas as pd
import sys
import toml
from addict import Dict
import seaborn as sns
from collections import OrderedDict
import numpy as np
from os.path import join
import os

sns.set(style="white")
sns.set_context("poster")


def sleep_bout_lengths(config):

    sleep_period = config.sleep_period
    original_bin_size = config.original_bin_size

    df = config.df

    # identify the 40s sleep bouts at each 10s timestamp if there has bee >=4 zero values,
    # add a 1 in the activity column
    def sleepscan(a):
        binsize = int(sleep_period / original_bin_size)
        ss = a.rolling(binsize).sum()
        y = ss == 0
        return y.astype(int)  # if numerical output is required
    df_sleep = pd.DataFrame(df[config.columns_to_use].apply(sleepscan))

    # Do we want each detector in a seperate file
    df_results = []
    for detector in config.columns_to_use:
        bouts = _boutscan(df_sleep[detector], detector)
        assert bouts.index.is_monotonic_increasing
        df_results.append(bouts)

    results: pd.DataFrame = pd.concat(df_results)
    results.set_index('start', inplace=True)
    results = results.sort_index()
    assert results.index.is_monotonic_increasing
    outpath = join(config.outdir, 'sleep_bout_lengths.csv')
    results.to_csv(outpath)

    sleep_bount_bins_by_pir(config, results)
    mean_sleep_bouts_per_bin_per_pir(config, df_sleep)


def _boutscan(series, id_):
    """
    Get sleep bout information.
    Parameters

    ----------
    series: pandas.Series 
        boolean sleep status
    Returns
    -------
    """
    start_times = []
    durations = []
    in_sleep_bout = False
    for i, sleep in enumerate(series.values):
        if sleep:
            if in_sleep_bout:
                continue
            else:
                in_sleep_bout = True
                start_times.append(series.index[i])
        elif not sleep:
            if in_sleep_bout:
                in_sleep_bout = False
                duration = series.index[i] - start_times[-1]
                durations.append(duration)
    # Any unfinished bouts
    if in_sleep_bout:
        duration = series.index[i] - start_times[-1]
        durations.append(duration)
    bouts_df = pd.DataFrame(dict(start=start_times, duration=durations))
    bouts_df['id'] = id_
    return bouts_df


def make_csv_of_sleep_bout_bins_by_pir(df, time, outdir):
    """
    # Make csv files. Each covering a stretch of 12hours, showing counts of sleep bount bins against PIR
    # New request from Gareth
    # split into 12 hour bins
    # make a pivot table such that rows are PIRs, columns are bins. and values are counts
    # results is a df with each sleep bout over 40 seconds giving PIR id and =bout duration
    Parameters
    ----------
    df
    time
    outdir

    Returns
    -------

    """
    bin_results = OrderedDict()
    df_less_than_5_mins = df[df.duration < pd.Timedelta(minutes=5)]
    bin_results['0-5'] = df_less_than_5_mins.groupby('id').size()
    bin_size = 5

    for t in range(5, 60, bin_size):
        lower_bound = t
        upper_bound = t + bin_size
        df_time_bin = df[(df.duration > pd.Timedelta(minutes=lower_bound))
                         & (df.duration < pd.Timedelta(minutes=upper_bound))]
        column_name = "{}-{}".format(lower_bound, upper_bound)
        bin_results[column_name] = df_time_bin.groupby('id').size()

    # Add the bin for anything over an hour
    df_over_60_mins = df[df.duration > pd.Timedelta(minutes=60)]
    bin_results['>1hr'] = df_over_60_mins.groupby('id').size()

    df_bin_results = pd.DataFrame.from_dict(bin_results)
    df_bin_results.fillna(0, inplace=True)
    bin_results_out = join(outdir, 'sleep_bout_bins_by_pir_{}.csv'.format(time))
    bin_results_out = bin_results_out.replace(':', '.')
    bin_results_out = bin_results_out.replace(' ', '_')
    # This replaces the colon in the drive path (eg C:) with a period on Windows. Need to change it back
    bin_results_out = bin_results_out.replace('.', ':', 1)  # '1' means max repalce 1. So just remove first '.'
    df_bin_results.to_csv(bin_results_out)


def sleep_bount_bins_by_pir(config, results):
    """
    TODO: doc what results is
    Split the data into 12 hour chunks and create a csv of sleep bout counts per bins per PIR
    
    Example output
    --------------
    ,0-5,5-10,10-15,15-20,20-25,25-30,30-35,35-40,40-45,45-50,50-55,55-60,>1hr
    PIR1,62,7,2,4.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
    PIR2,57,12,4,3.0,0.0,1.0,0.0,1.0,0.0,0.0,0.0,0.0,2.0
    PIR3,51,5,2,0.0,2.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
    PIR4,56,11,2,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
    PIR5,43,5,1,2.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
    PIR6,74,13,3,1.0,0.0,0.0,0.0,1.0,1.0,0.0,0.0,0.0,0.0
    PIR7,61,6,1,1.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
    PIR8,23,2,1,1.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
    """
    bin_by_pir_dir = join(config.outdir, 'sleep_bin_counts_by_pir')
    if not os.path.isdir(bin_by_pir_dir):
        os.mkdir(bin_by_pir_dir)

    d = pd.to_datetime(config.time_start)

    delta = pd.Timedelta(hours=12)

    # results.set_index(pd.to_datetime(results.start), inplace=True)
    assert results.index.is_monotonic_increasing

    while d <= pd.to_datetime(pd.to_datetime(config.time_end) - delta):

        d1 = str(d)
        d2 = str(d+delta)

        df_12h_chunk = results.loc[d1: d2]

        make_csv_of_sleep_bout_bins_by_pir(df_12h_chunk, str(d), bin_by_pir_dir)
        d += delta


def mean_sleep_bouts_per_bin_per_pir(config, df_sleep):
    """
    Creates a csv of mean sleep bout length per time bin per pir
    
    Example output
    --------------
    Time bin|,      PIR1, PIR2, PIR3 ....
    10:00: 10:30,   46s   52s   852   
    10:30: 11:00,   56s   76s   92s 

    """

    bin_length = config.time_bin_for_mean_sleep_bout_calculation_mins

    outfile = join(config.outdir, 'mean_sleep_bout_length_per_pir_{}_mins.csv'.format(bin_length))

    d = pd.to_datetime(config.time_start)

    delta = pd.Timedelta(minutes=bin_length)

    from collections import OrderedDict
    res_dict = OrderedDict()

    # Loop over the the time span in bin length chunks
    dfs = df_sleep # debigging
    while d <= pd.to_datetime(pd.to_datetime(config.time_end) - delta):

        # Get the start and end datetime in str format
        dt1 = str(d)
        dt2 = str(d + delta)

        # Do we want each detector in a seperate file
        bouts_results = []  # the bout start and duration per PIR
        sleep_bin_chunk = df_sleep.loc[dt1: dt2]

        for detector in config.columns_to_use:
            bouts = _boutscan(sleep_bin_chunk[detector], detector)
            bouts_results.append(bouts)

        bouts_df = pd.concat(bouts_results)

        if bouts_df.shape[0] > 0: # if dataframe has zero size, there are no sleep bouts for this chunck

            # set the index as the start time so we can truncate on it
            bouts_df.set_index(pd.to_datetime(bouts_df.start), inplace=True)
            # # Seems like I have to convert the timedelta to an int before we can do groupby+mean
            # bouts_df['duration'] = bouts_df['duration'].astype(int)

            bouts_df['duration'] = bouts_df['duration'] / np.timedelta64(1, 's')

            del bouts_df['start']
            gb_id = bouts_df.groupby(['id'])
            mean = gb_id.mean()

            # Convert the mean duration in ints back to a timedelta

            try:
                mean['duration'] = pd.to_timedelta(mean['duration'], unit='s').astype('timedelta64[s]')
            except TypeError as e:
               pass
            entry = mean['duration']
            res_dict[dt1] = entry
        d += delta
    res_df = pd.DataFrame.from_dict(res_dict, orient='index')
    # Not sure why the coluimns orders get mixed up
    res_df = res_df[config.columns_to_use]
    res_df.fillna(0, inplace=True)
    res_df.index.name = 'Bin time start'
    print(res_df)
    res_df.to_csv(outfile)


if __name__ == '__main__':
    config = Dict(toml.load(sys.argv[1]))
    sleep_bount_bins_by_pir(config)
    mean_sleep_bouts_per_bin_per_pir(config)