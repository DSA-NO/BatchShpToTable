# %%
import geopandas
from pathlib import Path
from tkinter import filedialog
import tkinter as tk
import sys
from typing import NamedTuple
from collections import namedtuple
import re
import pandas as pd
from shapely import wkb

import matplotlib.pyplot as plt
# import contextily as cx

import argparse
import time
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
        '-s', '--summary-map-pattern', type=str, default='',
        help='Creates a image with all shp files matching "s" summed. Remember to include <timestamp>_toteffout...')

    print("Remember to inluclude timstamp in pattern for doses!")

    args = parser.parse_args()
    start = time.process_time()

    if args.summary_map_pattern:
        args.summary_map_pattern = '*'+args.summary_map_pattern
    path = get_folder(args.input_folder)

    if args.pickle_file:
        df = pd.from_pickle(args.load_pickle)
    else:
        runs = get_runs(args, path)

        runs = parse_all_runs(args, runs)

        df = pd.concat(runs)
        df = df.groupby('geom_str').agg('sum')

        df.reset_index(inplace=True)

        df.to_pickle(f"{path.stem}{args.summary_map_pattern[1:]}_summary.pkl")
    print(time.process_time() - start)
    print(f"Final rows {len(df.index)}")

    df['geometry'] = df['geom_str'].apply(wkb.loads)
    df.plot(column='Value')
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
    for shp_file in path.glob(f"**/{args.summary_map_pattern}*.shp"):
        runname, timestamp, _ = parse_filename(shp_file)
        runs.setdefault(runname, {})
        runs[runname].setdefault(timestamp, [])
        runs[runname][timestamp].append(shp_file)
    return runs


def parse_run(timestamp, run, filelist, args):
    print(f"Reading {run}, {timestamp}")

    all_df = []

    if args.debug:
        print("DEBUG Truncating to 4")
        filelist = filelist[0:4]
    for file in filelist:
        _, _, key = parse_filename(file)
        print(f"\t{key.outputname} T:{key.timestep},E: {key.nuc_or_age} {file.name}")
        gdf = geopandas.read_file(file)
        if key.timestep > 0 and key.timestep < 48:
            # If the run stops before the first wanted timestep -> move value from "stop-timestep" to first wanted
            print(f"\tOverriding timestep {key.timestep}h to 48h")
        print(f"Rows {len(gdf.index)}")
        gdf['geom_str'] = gdf.geometry.apply(lambda x: wkb.dumps(x))
        gdf.drop(columns='geometry', inplace=True)
        all_df.append(gdf)

    return all_df


# %%
if __name__ == "__main__":
    # %%
    sys.argv = ["1",'-s' '876000_grid_gamratetot_bitmp_Total', '-i', 'indata/arp']
    # %%
    df = main()
    # %%
