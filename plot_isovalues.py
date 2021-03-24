# %%
import parse_all_runs
from pathlib import Path
import plot_summary
import geopandas
# %%
def toteff():
    filelist = open('toteff_files.txt').readlines()
    filelist = [Path(file.strip()) for file in filelist]

    class Args:
        plot = True
        debug = False

    for file in filelist:
        runname, timestamp, key = parse_all_runs.parse_filename(file)
        run = ''
        gdf = geopandas.read_file(file)
        isovalue_name = 'toteff'
        plot_summary.plot_valueisocurves(gdf,isovalue_name, timestamp)

# toteff()


#%%
def thyr():
    filelist = open('thyr_files_100cells.txt').readlines()
    filelist = [Path(file.strip()) for file in filelist]

    class Args:
        plot = True
        debug = False

    for file in filelist:
        runname, timestamp, key = parse_all_runs.parse_filename(file)
        run = ''
        gdf = geopandas.read_file(file)
        isovalue_name = 'thyr'
        plot_summary.plot_valueisocurves(gdf,isovalue_name, timestamp)

# thyr()

#%%
def i131():
    filelist = open('depo_files_i-131.txt').readlines()
    filelist = [Path(file.strip()) for file in filelist]

    class Args:
        plot = True
        debug = False

    for file in filelist:
        runname, timestamp, key = parse_all_runs.parse_filename(file)
        run = ''
        gdf = geopandas.read_file(file)
        isovalue_name = 'depo'
        plot_summary.plot_valueisocurves(gdf,isovalue_name, timestamp, name_extra='_i131_')

i131()