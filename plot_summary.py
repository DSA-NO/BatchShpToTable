# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import geopandas as gpd
import pandas as pd
from shapely import wkb
import mapclassify
import contextily as cx
import matplotlib.pyplot as plt
import matplotlib
import overlap
import sys

"""
Script that reads a pickle file and plots with a background map using contextily.

Using 'max' as aggregator show cells where the limit is ever exceeded IF .pkl is 0/1 based on criteria. 
Use 'max' or 'mean' on full input. 
"""
# Nordic flagbook criteria
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
# %%
def plot(run, criteria=''):
    # %%
    gdf = read_df(run)
    # %%
    run = run.replace(".pkl.bz2",'_')
    fig, ax = plt.subplots(dpi=250)  # figsize=(10, 10))

    gdf_out = gdf[gdf.Value > 0] # for speedup
    if criteria:
        gdf_out.Value = (gdf_out.Value > DOSE_CRITERIA_SI.get(criteria)).astype(int)

        # New zeros whrn criteria applied: 
        gdf_out = gdf_out[gdf_out.Value > 0]
    gdf_out = gdf_out.set_crs('EPSG:4326')

    gdf_out.to_crs('EPSG:25833', inplace=True)

    gdf_out.plot(ax=ax, edgecolor="face", linewidth=1)


    minx, miny, maxx, maxy = gdf_out.geometry.total_bounds
    padding_m = (maxx-minx)/100*100*.66
    ax.set_xlim(minx - padding_m, maxx + padding_m)
    ax.set_ylim(miny - padding_m, maxy + padding_m)

    #Add scale-bar
    x, y, scale_len = maxx+padding_m-2500, miny-padding_m+200, 2000 #arrowstyle='-'
    scale_rect = matplotlib.patches.Rectangle((x,y),scale_len,100,linewidth=0.5,edgecolor='k',facecolor='k')
    ax.add_patch(scale_rect)
    plt.text(x+scale_len/2, y+300, s='2 KM', fontsize=6, horizontalalignment='center')

    # Add release point
    releasepoint = overlap.create_point(overlap.GROTSUND_COORD)
    releasepoint.plot(ax=ax, color='k', marker='x', markersize=150)
    # plt.plot([overlap.GROTSUND_COORD[0]], [overlap.GROTSUND_COORD[1]], '+', color='black', markersize=15)


    basemap = cx.providers.CartoDB.Voyager
    #basemap = cx.providers.Stamen.Terrain
    cx.add_basemap(ax, crs="EPSG:25833", source=basemap,
                attribution=f"Bakgrunnskart: {basemap.attribution}", attribution_size=6)

    # ax.set_title('title')
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)

    # plt.savefig('sample.png', bbox_inches="tight", pad_inches=0)

    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    plt.tight_layout()
    fig.tight_layout()
    fig.canvas.start_event_loop(sys.float_info.min) #workaround for Exception in Tkinter callback

    fig.savefig(f"{run}{criteria}.png", bbox_inches='tight')
    print(f'Saved {run}{criteria}.png')
# %%
# %%

def notebook_dummy():
    """Run below cell and then cells inside plot()
    """
    # %%
    base = 'grotsund_arp_12h-100m_5km'
    run = f'{base}4800_grid_toteffout_bitmp_Adults_Total__full.pkl.bz2'
    criteria = 'evac'

    # %%
def create_all(base):
    # %%
    # Full sheltering
    run = f'{base}4800_grid_toteffout_bitmp_Adults_Total__full.pkl.bz2'
    plot(run, 'sheltering_full')


    # Partial sheltering
    run = f'{base}4800_grid_toteffout_bitmp_Adults_Total__full.pkl.bz2'
    plot(run, 'sheltering_partial')

    # Iodine  1 year old
    run = f'{base}hyrod_bitmp_1year_Tota__full.pkl.bz2'
    plot(run, 'iodine_child')

    # Iodine  Adult
    run = f'{base}hyrod_bitmp_Adults_Tota__full.pkl.bz2'
    plot(run, 'iodine_adult')

    # Evac adult
    run =f'{base}16800_grid_toteffout_bitmp_Adults_Total__full.pkl.bz2'
    plot(run, 'evac')


# %%
def plot_run_boundary():
    # %%
    from shapely.geometry import Polygon, mapping
    run = "run_boundary"
    ring = overlap.isocurve(65,overlap.GROTSUND_COORD)
    fig, ax = plt.subplots(dpi=250)  # figsize=(10, 10))

    ring = ring.set_crs('EPSG:4326')

    ring.to_crs('EPSG:25833', inplace=True)
    ring.geometry = [Polygon(mapping(x)['coordinates']) for x in ring.geometry]

    minx, miny, maxx, maxy = ring.geometry.total_bounds
    padding_m = (maxx-minx)/100*100*.13
    ax.set_xlim(minx - padding_m, maxx + padding_m)
    ax.set_ylim(miny - padding_m, maxy + padding_m)
    
    # #Add scale-bar
    x, y, scale_len = maxx+padding_m-25000, miny-padding_m+1200, 20000 #arrowstyle='-'
    scale_rect = matplotlib.patches.Rectangle((x,y),scale_len,100,linewidth=0.5,edgecolor='k',facecolor='k')
    ax.add_patch(scale_rect)
    plt.text(x+scale_len/2, y+1300, s='20 KM', fontsize=6, horizontalalignment='center')

    # Add release point

    ring.boundary.plot(ax=ax, edgecolor='black')#, color=None, edgecolor='k',linewidth = 2, )#facecolor=None)
    releasepoint= overlap.create_point(overlap.GROTSUND_COORD)
    releasepoint.plot(ax=ax,  marker='x', color='black')#, markersize=150, color=None, edgecolor='k',linewidth = 2, facecolor=None)

    basemap = cx.providers.CartoDB.Voyager
    #basemap = cx.providers.Stamen.Terrain
    # cx.add_basemap(ax, crs="EPSG:25833", source=basemap,
    #             attribution=f"Bakgrunnskart: {basemap.attribution}", attribution_size=6)

    # ax.set_title('title')
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)

    # plt.savefig('sample.png', bbox_inches="tight", pad_inches=0)

    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    plt.tight_layout()
    fig.tight_layout()
    fig.canvas.start_event_loop(sys.float_info.min) #workaround for Exception in Tkinter callback

    fig.savefig(f"{run}.png", bbox_inches='tight')
    print(f'Saved {run}.png')
    # %%


    # %%
if __name__ == '__main__':
    base5km = 'grotsund_arp_12h-100m_5km'
    base60km = 'grotsund_arp_12h-max'

    plot_run_boundary()

   
    # create_all(base5km)
    # create_all(base60km)
