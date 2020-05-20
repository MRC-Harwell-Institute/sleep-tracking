"""
Run all the scripts. Alternatively each script can be run seperately
"""
import sys

from scripts.sleep_counting import sleep_counting
from scripts.binning import binning
from scripts.cum_sleep_bout_figure import run
from scripts.sleep_bout_lengths import sleep_bout_lengths
from scripts import cfg_load

config_path = sys.argv[1]

config = cfg_load(config_path)
# binning(config)
# sleep_counting(config)
# sleep_bount_bins_by_pir(config)
# run(config)
sleep_bout_lengths(config)
