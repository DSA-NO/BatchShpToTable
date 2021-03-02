# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import geopandas as gpd
import pandas as pd
from shapely import wkb
import mapclassify
import contextily as cx
import matplotlib.pyplot as plt
import overlap

"""
Script that reads a pickle file and plots with a background map using contextily.

Using 'max' as aggregator show cells where the limit is ever exceeded IF .pkl is 0/1 based on critera. 
Use 'max' or 'mean' on full input. 
"""
# Nordic flagbook critera
DOSE_CRITERIA = {
    'iodine_child': 10,  # mGy end pf run
    'iodine_adult': 50,  # mGy end pf run
    'evac': 20, # 7 dager
    'sheltering_partial': 1, # mSv 2 dager
    'sheltering_full': 10,   # mSv 2 dager
        }
DOSE_CRITERIA_SI = {k:v/1000 for k,v in DOSE_CRITERIA.items() }

# %%
def dump_full_shp(run,df):
    gdf = gpd.GeoDataFrame(df)
    gdf['geometry'] = gdf['geom_str'].apply(wkb.loads)
    gdf = gdf[['Value','geometry']]
    gdf.to_file(f"{run}_full_shppackage.gpkg", layer='evac', driver="GPKG")

def read_df(run):
    df=pd.read_pickle(run)
    # dump_full_shp(run, df)
    df=df.groupby('geom_str').agg({'Value': 'max'})
    df.reset_index(inplace=True)

    gdf = gpd.GeoDataFrame(df)
    gdf['geometry'] = gdf['geom_str'].apply(wkb.loads)
    gdf = gdf[['Value','geometry']]

    # gdf.to_file(f"{run}_shp")

    return gdf

def plot(run, critera=''):

    gdf = read_df(run)
    run = run.replace(".pkl",'_')
    fig, ax = plt.subplots(dpi=250)  # figsize=(10, 10))

    gdf_out = gdf[gdf.Value > 0] # for speedup
    if critera:
        gdf_out.Value = (gdf_out.Value > DOSE_CRITERIA_SI.get(critera)).astype(int)

        # New zeros whrn critera applied: 
        gdf_out = gdf_out[gdf_out.Value > 0]
    gdf_out = gdf_out.set_crs('EPSG:4326')

    gdf_out.to_crs('EPSG:25833', inplace=True)

    gdf_out.plot(ax=ax)

    minx, miny, maxx, maxy = gdf_out.geometry.total_bounds

    padding_m = 9000
    ax.set_xlim(minx - padding_m, maxx + padding_m)
    ax.set_ylim(miny - padding_m, maxy + padding_m)

    basemap = cx.providers.CartoDB.Voyager
    #basemap = cx.providers.Stamen.Terrain
    cx.add_basemap(ax, crs="EPSG:25833", source=basemap,
                attribution=f"Bakgrunnskart: {basemap.attribution}", attribution_size=6)

    # ax.set_title('title')
    ax.set_xlabel('')
    ax.set_ylabel('')

    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    plt.tight_layout()

    fig.savefig(f"{run}{critera}.png")
    print(f'Saved {run}{critera}.png')

if __name__ == '__main__':
    base5km = 'grotsund_arp_12h-100m_5km'
    base60km = 'grotsund_arp_12h-max'


    def create_all(base):
        # Full sheltering
        run = f'{base}4800_grid_toteffout_bitmp_Adults_Total__full.pkl'
        plot(run, 'sheltering_full')


        # Partial sheltering
        run = f'{base}4800_grid_toteffout_bitmp_Adults_Total__full.pkl'
        plot(run, 'sheltering_partial')

        # Iodine  1 year old
        run = f'{base}hyrod_bitmp_1year_Tota__full.pkl'
        plot(run, 'iodine_child')

        # Iodine  Adult
        run = f'{base}hyrod_bitmp_Adults_Tota__full.pkl'
        plot(run, 'iodine_adult')

        # Evac adult
        run =f'{base}16800_grid_toteffout_bitmp_Adults_Total__full.pkl'
        plot(run, 'evac')
    
    create_all(base5km)
    create_all(base60km)