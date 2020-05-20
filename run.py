"""
Run all the scripts. Alternatively each script can be run seperately
"""
from .sleep_counting import sleep_counting
from .binning import binning
from .cum_sleep_bout_figure import run
from .sleep_bout_lengths import sleep_bount_bins_by_pir, mean_sleep_bouts_per_bin_per_pir
from .import cfg_load

config = cfg_load()
binning()
sleep_counting()
sleep_bount_bins_by_pir()
run()
sleep_bount_bins_by_pir()
mean_sleep_bouts_per_bin_per_pir()