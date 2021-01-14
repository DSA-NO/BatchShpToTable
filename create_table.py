"""
Creates a Excel-table based on max values found in Shape-files exported by Argos. 


Excel output example :
|                           | Endpoint         | depos_bitmp               | isocurve_arrival | thyrod_bitmp | toteffout_bitmp                             |
|---------------------------|------------------|-------------|-------------|------------------|--------------|-----------------|-------------|-------------|
|                           | Elapsed time [h] | 48          |             | 0                | 48           | 48              | 168         | 8760        |
|                           | Nuclide/Agegroup | Cs-137      | I-131       | total            | Total        | Total           | Total       | Total       |
| Run                       | Release date     |             |             |                  |              |                 |             |             |

| AnlopGrotsund_phase1_250m | 202005081553     | 70.1760726  | 403.5998708 | 48               | 1.45376E-05  | 2.18217E-06     | 2.74878E-06 | 6.75631E-06 |
|                           | 202005250235     | 32.06752642 | 184.2209984 | 48               | 6.31024E-06  | 9.60096E-07     | 1.21895E-06 | 3.04747E-06 |

Use:
    command line:
    python create_table.py <FOLDERNAME>
    GUI with folder selector: 
    python create_table.py 
"""

# %%
import pathlib
import re
from collections import namedtuple
import sys
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

import geopandas
import pandas as pd
import overlap
import pickle
#%%

COLUMN_NAMES = {'depos_bitmp': "Deposition [Bq/m2]",
                'toteffout_bitmp': 'Total effective dose [Sv]',
                'thyrod_bitmp': "Thyroid Organ Dose. Outdoor [Gy]",
                'gamratetot_bitmp': 'Dose rate [Sv/h]',
                }
DEBUG = False
SHP_MAX_MODE = False

def parse_filename(filepath):
    # Using the timestamp part of the string as splitter since the rest appears to change.
    # Regex that matches _202005081553_ in AnlopGrotsund_phase1_250m_202005081553_876000_grid_gamratetot_bitmp_Total
    filename = filepath.stem
    timestamp = re.findall(r"_[0-9]{12}_", filename)[0]
    runname, right_part = filename.split(timestamp)
    timestep = right_part.split("_")[0]
    nuclide = right_part.split("_")[-1]

    timestamp = timestamp.strip("_")
    outputname = right_part[len(timestep)+1:len(right_part)-len(nuclide)-1]
    outputname = outputname.split("grid_")[-1]

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
        # Total is assuemd when agegroup is given:
        nuclide= '' if nuclide == "Total" else nuclide
    else:
        agegroup = ''

    extra = f"{nuclide} {agegroup}"
    Run_metadata = namedtuple(
        "Run_metadata", ['outputname', 'timestep', 'extra'])
    key = Run_metadata(outputname=outputname, timestep=timestep, extra=extra)

    return runname, timestamp, key


def get_gdf_max(gdf):
    # with open(str(shpfile)+".txt", 'w') as testfile:
    #     testfile.write( str(gdf['Value'].max()))
    return {'top10': float(gdf['Value'].nlargest(10).mean()), 'max': float(gdf['Value'].max())}


def get_folder(run_folder="indata"):
    # Check for folder as argument. Cause we need 3 ways to select folder..
    if run_folder:
        run_folder = run_folder
    if len(sys.argv) > 1:
        run_folder = sys.argv[1]
    else:
        root = tk.Tk()
        root.withdraw()

        run_folder = filedialog.askdirectory(
            initialdir="C:/ARGOS-NT", title="Velg mappe for kjøring")

    path = Path(run_folder)
    return path


def main():
    import time
    start = time.process_time()

    # path = r"indata/Grotsund_phase1b_map/20200508T155300Z"
    path = r"C:\Utvikling\Argos\BatchShpToTable\indata\20200616T190500Z\Shape"
    path = pathlib.Path(path)

    # path = get_folder()
    runs = {}
    print(time.process_time() - start)
    for shp_file in path.glob("**/*.shp"):
        runname, timestamp, key = parse_filename(shp_file)

        runs.setdefault(runname, {})
        runs[runname].setdefault(timestamp, [])
        runs[runname][timestamp].append(shp_file)
    print(time.process_time() - start)
    df = pd.DataFrame()
    for r,(run, timestamps) in enumerate(runs.items()):
        print(f"Run {r}/{len(runs)}")
        for timestamp, filelist in timestamps.items():
            print(f"Reading {run}, {timestamp}")
            # Zeros are needed for pandas to accept these column nams when the rest are multiindex
            timestamp_results = {
                ('run', 0, '0'): run,
                ('timestamp', 0, '0'): timestamp}
            if DEBUG:
                print("DEBUG Truncating to 4")
                filelist = filelist[0:4]
            for file in filelist:
                _, _, key = parse_filename(file)
                print(f"\t{key.outputname} T:{key.timestep},E: {key.extra}")
                gdf = geopandas.read_file(file)

                if key.timestep > 0 and key.timestep < 48:
                    #If the run stops before the first wanted timestep -> move value from "stop-timestep" to first wanted
                    print(f"\tOverriding timestep {key.timestep}h to 48h")                    
                    key48 = key._replace(timestep=48)

                    #Warn that the key dosn't exist. Overwriting should not happen
                    if key48 in timestamp_results.keys():
                        print(
                            f"Warning, override 48h key already existing. {key}. \nOld:{timestamp_results[key48]}\nNew: {gdf['max']} ")
                        continue
                    else:
                        key = key48
                if SHP_MAX_MODE:
                    timestamp_results[key] = get_gdf_max(gdf)['max']
                else:
                    timestamp_results[key._replace(
                        extra=key.extra+"_tromsø")] = overlap.get_area_max(overlap.tromso_area, gdf)
                    timestamp_results[key._replace(
                        extra=key.extra+"2km")] = overlap.get_isocurve_max(2, overlap.GROTSUND_COORD, gdf)


            df = df.append(timestamp_results, ignore_index=True)
    df.to_pickle("temp.pkl")
    print(time.process_time() - start)
    #
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    df = df.reindex(
        sorted(df.columns, key=lambda x: (x[0], x[1], x[2])), axis=1)
    # Setting the indexes should be one step, but wont work..
    df = df.set_index(("run", 0, '0'))
    df = df.set_index(('timestamp', 0, '0'), append=True)
    df.index.rename(["Run", 'Release date'], inplace=True)

    #Rename stuff:
    df.rename_axis(
        ('Endpoint', 'Elapsed time [h]', 'Nuclide/Agegroup'), axis=1, inplace=True)
    df = df.rename(columns=COLUMN_NAMES)
    print(time.process_time() - start)

    df.to_excel(f"Max_values_{path.stem}.xlsx")
    print(time.process_time() - start)
    df.style.background_gradient(cmap='viridis')
    df.to_html('test.html')

if __name__ == "__main__":
    main()

# %%
