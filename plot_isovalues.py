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
        plot_summary.plot_valueisocurves(gdf, isovalue_name, timestamp)




def thyr(listfile = 'thyr_files_100cells.txt'):
    filelist = open(listfile).readlines()
    filelist = [Path(file.strip()) for file in filelist]

    class Args:
        plot = True
        debug = False

    for file in filelist:
        runname, timestamp, key = parse_all_runs.parse_filename(file)
        run = ''
        gdf = geopandas.read_file(file)
        isovalue_name = 'thyr'
        plot_summary.plot_valueisocurves(gdf, isovalue_name, timestamp)


def i131(listfile = 'depo_files_i-131.txt'):
    filelist = open(listfile).readlines()
    filelist = [Path(file.strip()) for file in filelist]

    class Args:
        plot = True
        debug = False

    for file in filelist:
        runname, timestamp, key = parse_all_runs.parse_filename(file)
        run = ''
        gdf = geopandas.read_file(file)
        isovalue_name = 'depo'
        plot_summary.plot_valueisocurves(
            gdf, isovalue_name, timestamp, name_extra='_i131_')


def reinsdyr(listfile = 'depo_files_i-131.txt'):
    filelist = open(listfile).readlines()
    filelist = [Path(file.strip()) for file in filelist]

    class Args:
        plot = True
        debug = False

    for file in filelist:
        runname, timestamp, key = parse_all_runs.parse_filename(file)
        run = ''
        gdf = geopandas.read_file(file)
        isovalue_name = 'rein'
        plot_summary.plot_valueisocurves(
            gdf, isovalue_name, timestamp, name_extra='_Cs134+137_Reinsdyr_')

# thyr() # alle
# reinsdyr('I131_fine.txt') 
# i131('I131_fine.txt') 
# reinsdyr()
# i131()
# toteff()


i131('i131_test.txt')