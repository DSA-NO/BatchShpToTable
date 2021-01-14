
import pathlib
import re
import sys
from pathlib import Path


import geopandas
import pandas as pd


def get_folder():
        # Check for folder as argument
    if len(sys.argv) > 1:
        run_folder = sys.argv[1]
    else:
        try:
            import tkinter as tk
            from tkinter import filedialog
            from tkinter.constants import NUMERIC
            root = tk.Tk()
            root.withdraw()

            run_folder = filedialog.askdirectory(
                initialdir="C:/ARGOS-NT", title="Velg mappe for kjøring")
        except:

            pass

    path = Path(run_folder)
    return path

def parse_filename(filepath):
    run_metadata = {'timestamp':'', 'runname': '', 'timestep':'','nuclide': '',  'outputname': '', 'agegroup':''}
    #Using the timestamp part of the string as splitter since the rest appears to change.
    #Regex that matches _202005081553_ in AnlopGrotsund_phase1_250m_202005081553_876000_grid_gamratetot_bitmp_Total
    filename = filepath.stem
    timestamp = re.findall(r"_[0-9]{12}_",filename)[0]
    runname, right_part = filename.split(timestamp)
    timestep  = right_part.split("_")[0]
    nuclide  = right_part.split("_")[-1]


    timestamp = timestamp.strip("_")
    outputname  = right_part[len(timestep)+1:len(right_part)-len(nuclide)-1]
    outputname = outputname.split("grid_")[-1]

    #Timestamp is in hours and seems to always end with 00, (might be minutes? :)..)
    timestep  = timestep[0:-2]
    AGEGROUPS = ['Adults', '1year', '5year', '10year','15year']
    if outputname.split("_")[-1] in AGEGROUPS:
        run_metadata['agegroup'] = outputname.split("_")[-1]
        outputname = outputname.split(run_metadata['agegroup'])[0].strip('_')
    run_metadata.update({'timestamp':timestamp, 'runname': runname, 'timestep':timestep,'nuclide': nuclide,  'outputname': outputname})

    return run_metadata

def get_shp_max(shpfile):
    gdf = geopandas.read_file(shpfile)
    return {'top10':float(gdf['Value'].nlargest(10).mean()), 'max': float(gdf['Value'].max())}


if __name__ == "__main__":    
    #path = get_folder()
    path = r"indata/Grotsund_phase1b_map/20200508T155300Z"
    pp=pathlib.Path(path)
    pp=pp.glob("**/*.shp")
    max_values = {}
    for x in pp:
        metadata = parse_filename(x)
        max_values.setdefault(metadata['outputname'],{})
        NUCLIDES = ['Cs-137', 'I-131', 'Sr-90', 'Total']
        if metadata['agegroup']:
            max_values[metadata['outputname']].setdefault(metadata['timestep'],{})
            max_values[metadata['outputname']][metadata['timestep']][metadata['agegroup']] = get_shp_max(x)
        elif metadata['nuclide']:
            if metadata['nuclide'] in NUCLIDES: 
                max_values[metadata['outputname']][metadata['nuclide']] = get_shp_max(x)
        # 
        #     print(metadata['outputname'],metadata['nuclide'], )
        #     max_values[metadata['outputname']][second_level][metadata['timestep']] = get_shp_max(x)
        # else:
    print(max_values)
    for key, item in max.items():
        if key ==  'toteffout_bitmp':
            # print(subitem1)
            for subkey1, subitem1 in item.get('48').items():
                print(key+"_48",subkey1, subitem1.get('max'))
            for subkey1, subitem1 in item.get('168').items():
                print(key+"_168",subkey1, subitem1.get('max'))
        elif key == 'thyrod_bitmp':
            for subkey1, subitem1 in item.get('48').items():
                print(key+"_48",subkey1, subitem1.get('max'))
        else:
            for subkey1, subitem1 in item.items():
                print(key,subkey1, subitem1.get('max'))
        #{(key, subkey1):subitem1['max']}
