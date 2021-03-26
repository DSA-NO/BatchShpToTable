"""
Creates a Excel file based on max values found in Shape files exported by Argos.   
"""

"""

Excel output example :
|                           | Endpoint         | depos_bitmp               | isocurve_arrival | thyrod_bitmp | toteffout_bitmp                             |
|---------------------------|------------------|-------------|-------------|------------------|--------------|-----------------|-------------|-------------|
|                           | Elapsed time [h] | 48          |             | 0                | 48           | 48              | 168         | 8760        |
|                           | Nuclide/Agegroup | Cs-137      | I-131       | total            | Total        | Total           | Total       | Total       |
| Run                       | Release date     |             |             |                  |              |                 |             |             |

| AnlopGrotsund_phase1_250m | 202005081553     | 70.1760726  | 403.5998708 | 48               | 1.45376E-05  | 2.18217E-06     | 2.74878E-06 | 6.75631E-06 |
|                           | 202005250235     | 32.06752642 | 184.2209984 | 48               | 6.31024E-06  | 9.60096E-07     | 1.21895E-06 | 3.04747E-06 |

"""

# %%
import re
from collections import namedtuple
from typing import NamedTuple
import sys
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import argparse
import time
import matplotlib.pyplot as plt

import geopandas
import pandas as pd
import overlap

# %%

class RunMetadata(NamedTuple):
    outputname: str
    timestep: str
    distance_km: float = None
    area: str = ''
    nuc_or_age: str = ''

RUNMETADATA_PROPER = ('Endpoint', 'Elapsed time [h]','Distance [km]','Area', 'Nuclide/Agegroup')


COLUMN_NAMES = {'depos_bitmp': "Deposition [Bq/m2]",
                'toteffout_bitmp': 'Total effective dose [Sv]',
                'thyrod_bitmp': "Thyroid Organ Dose. Outdoor [Gy]",
                'gamratetot_bitmp': 'Dose rate [Sv/h]',
                }
DISTANCES = {
    'short': [0.1, .2,.3, .4,.5, .6, .8, 1., 1.25, 1.5, 1.75, 2, 2.25, 2.5, 3, 3.5, 4, 4.5],
    'long' : [4, 6, 8, 10., 12, 15, 20, 30, 40, 50,60, 70, 80, 90]}



def parse_filename(filepath):
    # Row 1 in the shp contains the same data (- start time):
    # df.iloc[0]

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
    key = RunMetadata(outputname=outputname, timestep=timestep, nuc_or_age=extra)

    return runname, timestamp, key


def get_gdf_max(gdf):
    # with open(str(shpfile)+".txt", 'w') as testfile:
    #     testfile.write( str(gdf['Value'].max()))
    return {'top10': float(gdf['Value'].nlargest(10).mean()), 'max': float(gdf['Value'].max())}


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
        '-s','--summary-map-pattern', type=str, default='',
        help='Creates a image with all shp files matching "s" summed')
    parser.add_argument(
        '--distances',choices=DISTANCES.keys(), default='long',
        help=f'Isocurve distances to use')       


    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-m', '--shp-max-mode', action='store_true', default=False,
                       help='Get max values for entire SHP only')
    group.add_argument('-c', '--isocurve-shape-mode', action='store_true', default=False,
                       help='Get values at distances given in code. Center point and search area set in overlap.py')

    args = parser.parse_args()
    start = time.process_time()


    if args.summary_map_pattern:
        args.summary_map_pattern = '*'+args.summary_map_pattern
    path = get_folder(args.input_folder)

    print(time.process_time() - start)

    if args.pickle_file:
        df = pd.from_pickle(args.load_pickle)
    # elif args.summary_map_pattern:
    #     pass
    else:
        runs = get_runs(args, path)

        print(time.process_time() - start)

        rows = parse_all_runs(args, runs)

        df = pd.DataFrame(rows)
        print(time.process_time() - start)

        df.set_index(['run', 'timestamp'], inplace=True)
        df.index.rename(["Run", 'Release date'], inplace=True)

        df.columns = pd.MultiIndex.from_tuples(
            [tuple(x) for x in df.columns], names=RUNMETADATA_PROPER)

        # Sort columns by time, nuclide, distance , second and third... index. 
        df = df.reindex(
            sorted(df.columns, key=lambda x: (x[0], x[4], x[2], x[1])), axis=1)


        # Rename columns:
        df = df.rename(columns=COLUMN_NAMES)
        df.to_pickle(f"{path.stem}.pkl")
    print(time.process_time() - start)

    df.to_excel(f"output/Max_values_{path.stem}.xlsx")
    print(time.process_time() - start)
    # df.style.background_gradient(cmap='viridis')
    # df.to_html('test.html')
    return df

def parse_all_runs(args, runs):
    rows = []
    for r, (run, timestamps) in enumerate(runs.items()):
        print(f"Run {r}/{len(runs)}")
        for timestamp, filelist in timestamps.items():
            rows.append(parse_run(timestamp, run, filelist, args))
            print(len(rows))
    return rows

def get_runs(args, path):
    runs = {}
    for shp_file in path.glob(f"**/{args.summary_map_pattern}*.shp"):
        runname, timestamp, _ = parse_filename(shp_file)
        runs.setdefault(runname, {})
        runs[runname].setdefault(timestamp, [])
        runs[runname][timestamp].append(shp_file)
    return runs


def insert_isocurve_max(timestamp_results,key, distance, releasepoint, result_gdf ):                
    timestamp_results[key._replace(
        distance_km=distance)] = overlap.get_isocurve_max(distance, releasepoint, result_gdf)
    return timestamp_results
def parse_run(timestamp, run, filelist, args):
    print(f"Reading {run}, {timestamp}")

    timestamp_results = {
        'run': run,
        'timestamp': timestamp}
    if args.debug:
        print("DEBUG Truncating to 4")
        filelist = filelist[0:4]
    for file in filelist:
        _, _, key = parse_filename(file)
        print(f"\t{key.outputname} T:{key.timestep},E: {key.nuc_or_age}")
        if file == Path("E:/ArgosBatch/grotsund_arp_12h-max/20200401T010000Z/Shape/grotsund_arp_12h-max_202004010100_2718_grid_depos_bitmp_I-131.shp"):
            print("skipped")
            return timestamp_results
        gdf = geopandas.read_file(file)
        if args.shp_max_mode:
            timestamp_results[key] = get_gdf_max(gdf)['max']
        else:
            for distance in DISTANCES.get(args.distances):
                timestamp_results = insert_isocurve_max(timestamp_results,key,
                                                        distance, overlap.GROTSUND_COORD, gdf)

    return timestamp_results


# %%

if __name__ == "__main__":
    # Slice by nested:
    # df.loc[:,(slice(None),slice(None), 'Cs-137  0.2km')]
    # sys.argv = "dummy -i E:\ArgosBatch\grotsund_arp_12h-max -c".split()
    # Område med 2000kBq/m2 - Reinsdyr:
    sys.argv = "dummy -i E:\ArgosBatch\grotsund_arp_12h-max -s grid_depos_bitmp_I-131 --distances long -c".split()

    # breaking:
    # sys.argv = "dummy -i E:/ArgosBatch/grotsund_arp_12h-max/20200401T010000Z/Shape -s grid_depos_bitmp_I-131 --distances long -c".split()
    #for notebook:
    # 
    df = main()

def notebook_args():
    # %%
    """Dummy for notebook argsparse. Run first"""
    sys.argv = ['dummy', "-c", "-i",
                "indata\\20200616T190500Z\\Shape"]
                
    # %%


def create_summary():
    """Dummy function for notebooks
    """
    # %%
    def percentile(n):
        def percentile_(x):
            return x.quantile(n)
        percentile_.__name__ = 'percentile_{:2.0f}'.format(n*100)
        return percentile_
        
    df= pd.read_pickle("grotsund_arp_12h-max.pkl")
    # 5 og 95 percentil, cou
    df2=df.agg(('min','mean','max', 'median',percentile(.05), percentile(.95),  'count')).transpose()
    df2.to_excel("/mnt/hgfs/Utvikling/Argos/BatchShpToTable/grotsund_arp_12h-max.xlsx")
    # %%


# %%
