import pandas as pd
import settings as config
from os.path import join


def bining():
    time_start = config.time_start
    time_end = config.time_end


    # read in the time series data
    df = pd.read_csv(config.data_abs_path, index_col=False)

    df = config.df

    #Take a peak to check
    print('unbinned data')
    print(df[0:12])

    # Resample by x minutes.
    resampled_df = df.resample('{}T'.format(config.new_bin_size_mins)).mean()

    print('resampled data')
    print(resampled_df[0:3])

    outpath = config.outdir / 'binned_{}_mins.csv'.format(config.new_bin_size_mins)

    resampled_df.to_csv(outpath)

if __name__ == '__main__':
    bining()