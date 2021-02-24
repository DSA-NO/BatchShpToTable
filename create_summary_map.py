# %%
import pandas as pd
import overlap
import matplotlib.pyplot as plt
import contextily as cx
import shapely
from shapely.geometry import Polygon, mapping
from create_table import parse_filename, parse_all_runs 
import argparse
# %%
def def main():
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
        help='Creates a image with all shp files matching "s" summed')


args = parser.parse_args()


def get_runs(args, path):
    runs = {}
    for shp_file in path.glob(f"**/{args.summary_map_pattern}*.shp"):
        runname, timestamp, _ = parse_filename(shp_file)
        runs.setdefault(runname, {})
        runs[runname].setdefault(timestamp, [])
        runs[runname][timestamp].append(shp_file)
    return runs

if __name__ == "__main__":
    main()
    pass