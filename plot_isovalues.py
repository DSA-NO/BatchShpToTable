"""Plot runs one by one based on a list of files in tge given `listfile`. Colors the plot based on value/critera in argos_colormaps.py """
# %%
import parse_all_runs
from pathlib import Path
import plot_summary
import geopandas
# %%

def toteff(listfile = 'toteff_files.txt'):
    filelist = open(listfile).readlines()
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
# toteff('toteff_final.txt')
reinsdyr('eks4.txt')
i131('eks4.txt')

# i131('i131_fine.txt')
