import toml
from os.path import join, realpath, dirname
import pandas as pd
from pathlib import Path
import addict
import sys


def load_config(config_path) -> addict.Dict:
    """
    Load the toml config, load the sleep data. Return the addict config.

    Parameters
    ----------
    config_path

    Returns
    -------

    """
    config = addict.Dict(toml.load(config_path))
    # Convert to time-aware stamps
    config.time_start = pd.to_datetime("2017-03-16 11:00:00").tz_localize('UTC')
    config.time_end = pd.to_datetime("2017-03-23 11:00:00").tz_localize('UTC')

    config_dir = Path(config_path).parent
    config.data_abs_path = join(config_dir, config.data_path)

    # Make the outdir
    config.outdir = config_dir / config.outdir
    Path(config.outdir).mkdir(exist_ok=True)

    # read in the time series data
    df = pd.read_csv(config.data_abs_path)
    # TODO: complain if not found
    # Delete the unused columns
    df.drop(config.columns_to_remove, axis=1, inplace=True)

    # Convert timestamp to DateTime objects
    df = df.set_index(pd.to_datetime(df.Time))
    del df['Time']

    if not _monotinic_increasing(df):
        sys.exit('Exitied as time stops are not monotonic increasing')

    # Truncate to specified time range
    df = df.truncate(before=config.time_start, after=config.time_end)
    if df.size < 1:
        sys.exit('dataframe has zero size. Is the datetime range correct?')
    config.df = df

    return config


def _monotinic_increasing(df):
    # check whether time stamps are monotonic increaseing and print indices where it's not
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




