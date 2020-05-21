"""
Run all the scripts. Alternatively each script can be run seperately
"""
import sys

from scripts.sleep_counting import sleep_counting
from scripts.binning import binning
from scripts.cum_sleep_bout_figure import run
from scripts.sleep_bout_lengths import sleep_bout_lengths
from scripts.cfg_load import load_config

config_path = sys.argv[1]

config = load_config(config_path)

# Completes
# binning(config)

# Completes
# sleep_counting(config)

#Completes
# sleep_bout_lengths(config)


run(config)

# Completes
# sleep_bout_lengths(config)
