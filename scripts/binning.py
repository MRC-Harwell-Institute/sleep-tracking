import pandas as pd
from os.path import join


def binning(config):

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
    binning()