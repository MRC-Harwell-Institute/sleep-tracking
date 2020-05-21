#! /usr/bin/env python3

"""
Run all the scripts. The single argument is the config file. See sleep.toml for an example.
Alternatively, each script can be run sperately from the command line.

Example
-------
    $ python3 run_sleep_scripts.py sleep.toml
"""
import sys

from scripts.sleep_counting import sleep_counting
from scripts.binning import binning
from scripts.cum_sleep_bout_figure import cum_sleep_bouts_fig
from scripts.sleep_bout_lengths import sleep_bout_lengths
# from scripts.cfg_load import load_config

# config_path = sys.argv[1]

# config = load_config(config_path)

# binning(config)
#
sleep_counting('')
#
# sleep_bout_lengths(config)
#
# cum_sleep_bouts_fig(config)
#
# sleep_bout_lengths(config)
