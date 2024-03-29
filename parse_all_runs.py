"""
Parses all shape files and stores the complete grid in a dataframe
"""
import argparse
# from collections import namedtuple
import re
import sys
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import NamedTuple

# %%
import geopandas
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from shapely import wkb

# import contextily as cx


# %%
class RunMetadata(NamedTuple):
    outputname: str
    timestep: str
    distance_km: float = None
    area: str = ''
    nuc_or_age: str = ''


def parse_filename(filepath):
    # Using the timestamp part of the string as splitter since the rest appears to change.
    # Regex that matches _202005081553_ in AnlopGrotsund_phase1_250m_202005081553_876000_grid_gamratetot_bitmp_Total
    filename = filepath.stem
    timestamp = re.findall(r"_[0-9]{12}_", filename)[0]
    runname, right_part = filename.split(timestamp)
    timestep = right_part.split("_")[0].strip()
    nuclide = right_part.split("_")[-1].strip()

    timestamp = timestamp.strip("_")
    outputname = right_part[len(timestep)+1:len(right_part)-len(nuclide)-1]
    outputname = outputname.split("grid_")[-1].strip()

    # Timestamp is in hours and seems to always end with extra 00, (might be minutes? :)..)
    timestep = timestep[0:-2]
    try:
        timestep = int(timestep)
    except:
        pass

    AGEGROUPS = ['Adults', '1year', '5year', '10year', '15year']
    if outputname.split("_")[-1] in AGEGROUPS:
        agegroup = outputname.split("Total")[0].split("_")[-1]
        outputname = outputname.split(agegroup)[0].strip('_')
        # Total is assumed when agegroup is given:
        nuclide = '' if nuclide == "Total" else nuclide
    else:
        agegroup = ''

    extra = f"{nuclide} {agegroup}"
    key = RunMetadata(outputname=outputname,
                      timestep=timestep, nuc_or_age=extra)

    return runname, timestamp, key


def get_folder(run_folder):
    """Retur folder as a path object or open selector GUI if no folder selected
    """
    if not run_folder:
        root = tk.Tk()
        root.withdraw()

        run_folder = filedialog.askdirectory(
            initialdir="C:/ARGOS-NT", title="Velg mappe for kjøring")

    path = Path(run_folder)
    return path


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-i', '--input-folder', type=str, default=r"indata/Shape",
        help='Folder with runs')
    parser.add_argument(
        '-p', '--pickle_file', type=str, default=None,
        help='Load a pickled dataframe instead of reading SHPs')
    parser.add_argument(
        '-d', '--debug', action='store_true', default=False,
        help='Debug')
    parser.add_argument(
        '-pl', '--plot', action='store_true', default=False,
        help='Plot every shp to png')
    parser.add_argument(
        'summary_pattern', type=str,
        help='Creates an image with all shp files matching "s" summed. Remember to include <timestamp>_toteffout...')


    print("Remember to inluclude timstamp in pattern for doses!")

    args = parser.parse_args()
    start = time.process_time()

    if args.summary_pattern:
        args.summary_pattern = '*'+args.summary_pattern
    path = get_folder(args.input_folder)

    if args.pickle_file:
        df = pd.from_pickle(args.load_pickle)
    else:
        runs = get_runs(args, path)

        runs = parse_all_runs(args, runs)

        df = pd.concat(runs)

        df.reset_index(inplace=True)

        outfile_full= f"{path.stem}{args.summary_pattern[1:]}__full.pkl.bz2"
        df.to_pickle(outfile_full
            )
        print(f"written {outfile_full}")

    df = df.groupby('geom_str').agg('sum')
    df.to_pickle(
                f"{path.stem}{args.summary_pattern[1:]}__summary.pkl")
    print(time.process_time() - start)
    print(f"Final rows {len(df.index)}")
    df.reset_index(inplace=True)


    df.drop(columns='geom_str', inplace=True)
    
    return df


def parse_all_runs(args, runs):
    all_results = []
    for r, (run, timestamps) in enumerate(runs.items()):
        print(f"Run {r}/{len(runs)}")
        for timestamp, filelist in timestamps.items():
            all_results.extend(parse_run(timestamp, run, filelist, args))
    return all_results


def get_runs(args, path):
    runs = {}
    for shp_file in path.glob(f"**/{args.summary_pattern}*.shp"):
        runname, timestamp, _ = parse_filename(shp_file)
        runs.setdefault(runname, {})
        runs[runname].setdefault(timestamp, [])
        runs[runname][timestamp].append(shp_file)
    return runs

def log_filename(isovalue_name:str, filename):
    with open(f"{isovalue_name}_files.txt", 'a') as ofile:
        ofile.write(str(filename)+ '\n')

def isovalues_above(gdf, isovalue_name, modifier = 1000):

    import argos_colormaps

    isovalues: dict = getattr(argos_colormaps,isovalue_name)
    isovalue_modifier = getattr(argos_colormaps, isovalue_name+"_modifier")
    bins = list(isovalues.keys())


    # Transform mSv/kBq:
    gdf.Value = gdf.Value*isovalue_modifier
    gdf = gdf[gdf.Value > min(bins)]
    print(len(gdf.index))
    if len(gdf.index) > 1500:
        return True

def parse_run(timestamp, run, filelist, args):
    import plot_summary
    if not args.plot:
        print(f"Reading {run}, {timestamp}")

    all_df = []
    if args.debug:
        print("DEBUG Truncating to 4")
        filelist = filelist[0:4]
    for file in filelist:
        _, _, key = parse_filename(file)
        gdf = geopandas.read_file(file)
        if args.plot:
            # plot_iso(gdf, timestamp)
            isovalue_name = 'depo'
            # plot_summary.plot_valueisocurves(gdf,isovalue_name, timestamp)
            printed_ok =isovalues_above(gdf, isovalue_name)
            if printed_ok:log_filename(isovalue_name, file)


        else:
            print(f"\t{key.outputname} T:{key.timestep},E: {key.nuc_or_age} {file.name}")
            print(f"Rows {len(gdf.index)}")
            gdf['geom_str'] = gdf.geometry.apply(lambda x: wkb.dumps(x))
            # gdf.drop(columns='geometry', inplace=True)
            gdf = gdf[['Value', 'geom_str']]


            all_df.append(gdf)

    return all_df


# %%
if __name__ == "__main__":
    # %%
    # sys.argv = ["1", '876000_grid_gamratetot_bitmp_Total',
    #             '-i', 'indata/arp']


    # Example inputs:
    # I-131 coarse to pickle:
    #sys.argv = r"dummy grid_depos_bitmp_I-131 -i E:\ArgosBatch\grotsund_arp_12h-max\ ".split()  

    # TYR:
    # sys.argv = "dummy grid_thyrod_bitmp_1year_Total -i E:\ArgosBatch\grotsund_arp_12h-100m_5km -pl".split()
    # I-131 Grov
    # sys.argv = "dummy grid_depos_bitmp_I-131 -i E:\ArgosBatch\grotsund_arp_12h-max\ -pl".split()    
    # I-131 Fin
    # sys.argv = "dummy grid_depos_bitmp_I-131 -i E:\ArgosBatch\grotsund_arp_12h-100m_5km -pl".split()
    
    # sys.argv = r"1 4800_grid_toteffout_bitmp_Adults_Total -i E:\ArgosBatch\grotsund_arp_12h-100m_5km\20200617T070000Z -pl".split() # single
    # %%
    df = main()
    # %%
