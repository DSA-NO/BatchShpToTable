"""
Script that reads a pickle file and plots with a background map using contextily.

Using 'max' as aggregator show cells where the limit is ever exceeded IF .pkl is 0/1 based on criteria. 
Use 'max' or 'mean' on full input. 
"""
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

# Nordic flagbook criteria
DOSE_CRITERIA = {
    'iodine_child': 10,  # mGy end pf run
    'iodine_adult': 50,  # mGy end pf run
    'evac': 20,  # 7 dager
    'sheltering_partial': 1,  # mSv 2 dager
    'sheltering_full': 10,   # mSv 2 dager
}
DOSE_CRITERIA_SI = {k: v/1000 for k, v in DOSE_CRITERIA.items()}

# %%


def dump_full_shp(run, df):
    gdf = gpd.GeoDataFrame(df)
    gdf['geometry'] = gdf['geom_str'].apply(wkb.loads)
    gdf = gdf[['Value', 'geometry']]
    gdf.to_file(f"{run}_full_shppackage.gpkg", layer='evac', driver="GPKG")


def read_df(run):
    df = pd.read_pickle(run)
    # dump_full_shp(run, df)
    df = df.groupby('geom_str').agg({'Value': 'max'})
    df.reset_index(inplace=True)

    gdf = gpd.GeoDataFrame(df)
    gdf['geometry'] = gdf['geom_str'].apply(wkb.loads)
    gdf = gdf[['Value', 'geometry']]

    # gdf.to_file(f"{run}_shp")

    return gdf
# %%


def get_areas_above(run, criteria):
    gdf = read_df(run)
    gdf_out = gdf[gdf.Value > 0]  # for speedup
    if criteria:
        gdf_out.Value = (
            gdf_out.Value > DOSE_CRITERIA_SI.get(criteria)).astype(int)

        # New zeros whrn criteria applied:
        gdf_out = gdf_out[gdf_out.Value > 0]
    gdf_out = gdf_out.set_crs('EPSG:4326')

    gdf_out.to_crs('EPSG:25833', inplace=True)
    return gdf_out


def plot(run, criteria=''):
    # %%
    fig, ax = plt.subplots(dpi=250)  # figsize=(10, 10))

    gdf_out = get_areas_above(run, criteria)
    gdf_out.plot(ax=ax, edgecolor="face", linewidth=1)

    run = run.replace(".pkl.bz2", '_')

    minx, miny, maxx, maxy = gdf_out.geometry.total_bounds
    padding_m = (maxx-minx)/100*100*.66
    ax.set_xlim(minx - padding_m, maxx + padding_m)
    ax.set_ylim(miny - padding_m, maxy + padding_m)

    # Add scale-bar
    x, y, scale_len = maxx+padding_m-2500, miny - \
        padding_m+200, 2000  # arrowstyle='-'
    scale_rect = matplotlib.patches.Rectangle(
        (x, y), scale_len, 100, linewidth=0.5, edgecolor='k', facecolor='k')
    ax.add_patch(scale_rect)
    plt.text(x+scale_len/2, y+300, s='2 KM',
             fontsize=6, horizontalalignment='center')

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
    ax.tick_params(left=False, labelleft=False,
                   bottom=False, labelbottom=False)

    # plt.savefig('sample.png', bbox_inches="tight", pad_inches=0)

    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    plt.tight_layout()
    fig.tight_layout()
    # workaround for Exception in Tkinter callback
    fig.canvas.start_event_loop(sys.float_info.min)

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
    plot_CM(run, 'sheltering_full')

    # Partial sheltering
    run = f'{base}4800_grid_toteffout_bitmp_Adults_Total__full.pkl.bz2'
    plot_CM(run, 'sheltering_partial')

    # Iodine  1 year old
    run = f'{base}hyrod_bitmp_1year_Tota__full.pkl.bz2'
    plot_CM(run, 'iodine_child')

    # Iodine  Adult
    run = f'{base}hyrod_bitmp_Adults_Tota__full.pkl.bz2'
    plot_CM(run, 'iodine_adult')

    # Evac adult
    run = f'{base}16800_grid_toteffout_bitmp_Adults_Total__full.pkl.bz2'
    plot_CM(run, 'evac')


# %%
def plot_run_boundary65km():
    # %%
    from shapely.geometry import Polygon, mapping
    run = "run_boundary65km"
    ring = overlap.isocurve(65, overlap.GROTSUND_COORD)
    fig, ax = plt.subplots(dpi=250)  # figsize=(10, 10))

    ring = ring.set_crs('EPSG:4326')

    ring.to_crs('EPSG:25833', inplace=True)
    ring.geometry = [Polygon(mapping(x)['coordinates']) for x in ring.geometry]

    minx, miny, maxx, maxy = ring.geometry.total_bounds
    padding_m = (maxx-minx)/100*100*.13
    ax.set_xlim(minx - padding_m, maxx + padding_m)
    ax.set_ylim(miny - padding_m, maxy + padding_m)

    # #Add scale-bar
    x, y, scale_len = maxx+padding_m-25000, miny - \
        padding_m+1200, 20000  # arrowstyle='-'
    scale_rect = matplotlib.patches.Rectangle(
        (x, y), scale_len, 100, linewidth=0.5, edgecolor='k', facecolor='k')
    ax.add_patch(scale_rect)
    plt.text(x+scale_len/2, y+1300, s='20 KM',
             fontsize=6, horizontalalignment='center')

    # Add release point

    # , color=None, edgecolor='k',linewidth = 2, )#facecolor=None)
    ring.boundary.plot(ax=ax, edgecolor='black')
    releasepoint = overlap.create_point(overlap.GROTSUND_COORD)
    # , markersize=150, color=None, edgecolor='k',linewidth = 2, facecolor=None)
    releasepoint.plot(ax=ax,  marker='x', color='black')

    basemap = cx.providers.CartoDB.Voyager
    #basemap = cx.providers.Stamen.Terrain
    cx.add_basemap(ax, crs="EPSG:25833", source=basemap,
                   attribution=f"Bakgrunnskart: {basemap.attribution}", attribution_size=6)

    # ax.set_title('title')
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False,
                   bottom=False, labelbottom=False)

    # plt.savefig('sample.png', bbox_inches="tight", pad_inches=0)

    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    plt.tight_layout()
    fig.tight_layout()
    # workaround for Exception in Tkinter callback
    fig.canvas.start_event_loop(sys.float_info.min)

    fig.savefig(f"{run}.png", bbox_inches='tight')
    print(f'Saved {run}.png')
    # %%


def get_ring(countermeasure, level='maks'):
    from shapely.geometry import Polygon, mapping
    distances = {
        "Matproduksjon": {
            "maks": 55.0,
            "95-persentil": 55.0
        },
        "sheltering_full": {
            "maks": 2.5,
            "95-persentil": 0.8
        },
        "sheltering_partial": {
            "maks": 5.0,
            "95-persentil": 4.0
        },
        "evac": {
            "maks": 1.75,
            "95-persentil": 0.5
        },
        "iodine_child": {
            "maks": 9.0,
            "95-persentil": 4.0
        },
        "iodine_adult": {
            "maks": 3.0,
            "95-persentil": 1.5
        }
    }
    ring = overlap.isocurve(
        distances[countermeasure][level], overlap.GROTSUND_COORD)

    ring = ring.set_crs('EPSG:4326')

    ring.to_crs('EPSG:25833', inplace=True)
    ring.geometry = [Polygon(mapping(x)['coordinates']) for x in ring.geometry]

    return ring


def plot_CM(run='', countermeasure=''):
    # %%
    fig, ax = plt.subplots(dpi=100)  # figsize=(10, 10))

    if run:
        gdf_out = get_areas_above(run, countermeasure)
        gdf_out.plot(ax=ax, edgecolor="face", linewidth=1)

        run = countermeasure + '_' + run.replace(".pkl.bz2", '')
    else:
        run = "tiltak_"+countermeasure

    ring = get_ring(countermeasure, 'maks')
    ring.boundary.plot(ax=ax, edgecolor='black', linestyle=':',)

    ring = get_ring(countermeasure, '95-persentil')
    ring.boundary.plot(ax=ax, edgecolor='black', linestyle='-',)

    ring = get_ring(countermeasure)
    ring.boundary.plot(ax=ax, edgecolor='black', linestyle=':',)

    minx, miny, maxx, maxy = ring.geometry.total_bounds
    padding_m = (maxx-minx)/100*100*.15
    ax.set_xlim(minx - padding_m, maxx + padding_m)
    ax.set_ylim(miny - padding_m, maxy + padding_m)

    # Add scale-bar
    if maxx-minx < 15000:
        scale_m = 2000
    elif maxx-minx < 40000:
        scale_m = 5000
    else:
        scale_m = 20000

    x = maxx + padding_m - (maxx - minx)*0.015 - scale_m
    y = miny - padding_m + (maxy - miny)*.015

    # y  =  miny*0.9999999460
    scale_line = matplotlib.patches.Arrow(
        x, y, scale_m, 0, linewidth=1, edgecolor='k', facecolor='k')
    ax.add_patch(scale_line)
    plt.text(x+scale_m/2, y+(maxy - miny)*.01, s=f'{scale_m/1000:.0f} Km',
             horizontalalignment='center')  # fontsize=6,

    # Add release point
    releasepoint = overlap.create_point(overlap.GROTSUND_COORD)
    releasepoint.plot(ax=ax,  marker='x', color='black')

    # basemap = cx.providers.CartoDB.Voyager
    #basemap = cx.providers.Stamen.Terrain
    graatone = {'url': "https://opencache.statkart.no/gatekeeper/gk/gk.open_gmaps?layers=norges_grunnkart_graatone&zoom={z}&x={x}&y={y}",
                'attribution': '© Kartverket'}
    grunnkart = {'url': "https://opencache.statkart.no/gatekeeper/gk/gk.open_gmaps?layers=norges_grunnkart&zoom={z}&x={x}&y={y}",
                 'attribution': '© Kartverket'}

    basemap = grunnkart
    attrib = f"Bakgrunnskart: {basemap['attribution']}"
    # attribution_size=6)  # , zoom=15)
    cx.add_basemap(ax, crs="EPSG:25833", source=basemap, attribution=attrib,)

    # ax.set_title('title')
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False,
                   bottom=False, labelbottom=False)

    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    plt.tight_layout()
    fig.tight_layout()

    # workaround for Exception in Tkinter callback:
    fig.canvas.start_event_loop(sys.float_info.min)

    fig.savefig(f"{run}.png", bbox_inches='tight')
    print(f'Saved {run}.png')
    # %%


def plot_valueisocurves(gdf, isovalue_name: str = 'toteff', timestamp='', ring=False, name_extra=''):
    # %%
    # gdf = geopandas.read_file(r"E:\ArgosBatch\grotsund_arp_12h-100m_5km\20200617T070000Z\Shape\grotsund_arp_12h-100m_5km_202006170700_4800_grid_toteffout_bitmp_Adults_Total.SHP")
    # timestamp = '1'
    # %%
    import argos_colormaps

    isovalues: dict = getattr(argos_colormaps, isovalue_name)
    isovalue_modifier = getattr(argos_colormaps, isovalue_name+"_modifier")
    cmap = matplotlib.colors.ListedColormap(isovalues.values())

    bins = list(isovalues.keys())+[float("inf")]
    # %%
    # gdf = geopandas.read_file(r"E:\ArgosBatch\grotsund_arp_12h-100m_5km\20200617T160000Z\Shape\grotsund_arp_12h-100m_5km_202006171600_4800_grid_toteffout_bitmp_Adults_Total.shp")
    fig, ax = plt.subplots(dpi=100)  # figsize=(10, 10))

    # Transform Sv to mSv:
    gdf.Value = gdf.Value*isovalue_modifier
    gdf = gdf[gdf.Value > min(bins)]
    if len(gdf.index) > 3:
        gdf = gdf.to_crs('EPSG:25833')
        # last one if 'inf' to make bins "larger than.."
        labels = [f">{x}" for x in bins[:-1]]
        gdf['cat'] = pd.cut(gdf['Value'], bins=bins,
                            labels=labels, right=False)

        gdf.plot(ax=ax, column='cat',
                 edgecolor='none',
                 # alpha=0.9,
                 cmap="magma_r",
                 legend=True,
                 legend_kwds={'loc': 'lower left', 'bbox_to_anchor': (1.0, 0)}
                 # legend_kwds={'label': 'Dose [mSv]'}
                 )

        # ring = get_ring(countermeasure, 'maks')
        # ring.boundary.plot(ax=ax, edgecolor='black', linestyle=':',)
        FIXED_AREA = False
        if FIXED_AREA:
            minx = 658754  # grøtsund lokalt
            miny = 7742093
            maxx = 661589
            maxy = 7744187
            padding_m = 0
        else:
            minx, miny, maxx, maxy = gdf.geometry.total_bounds
            padding_m = (maxx-minx)/100*100*1
        ax.set_xlim(minx - padding_m, maxx + padding_m)
        ax.set_ylim(miny - padding_m, maxy + padding_m)

        # Add scale-bar
        if maxx-minx < 2000:
            scale_m = 100
            scale_str = "100 m"
        if maxx-minx < 6000:
            scale_m = 500
            scale_str = "500 m"
        elif maxx-minx < 15000:
            scale_m = 2000
            scale_str = "2 Km"
        elif maxx-minx < 40000:
            scale_m = 5000
            scale_str = "5 Km"
        else:
            scale_m = 20000
            scale_str = "20 Km"

        x = maxx + padding_m - (maxx - minx)*0.015 - scale_m
        y = miny - padding_m + (maxy - miny)*.015

        # y  =  miny*0.9999999460
        scale_line = matplotlib.patches.Arrow(
            x, y, scale_m, 0, linewidth=1, edgecolor='k', facecolor='k')
        ax.add_patch(scale_line)
        plt.text(x+scale_m/2, y+(maxy - miny)*.01, s=scale_str,
                 horizontalalignment='center')  # fontsize=6,

        # # Add release point
        # releasepoint = overlap.create_point(overlap.GROTSUND_COORD)
        # releasepoint.plot(ax=ax,  marker='x', color='black')

        # basemap = cx.providers.CartoDB.Voyager
        #basemap = cx.providers.Stamen.Terrain
        graatone = {'url': "https://opencache.statkart.no/gatekeeper/gk/gk.open_gmaps?layers=norges_grunnkart_graatone&zoom={z}&x={x}&y={y}",
                    'attribution': '© Kartverket'}
        grunnkart = {'url': "https://opencache.statkart.no/gatekeeper/gk/gk.open_gmaps?layers=norges_grunnkart&zoom={z}&x={x}&y={y}",
                     'attribution': '© Kartverket'}

        basemap = grunnkart
        attrib = f"Bakgrunnskart: {basemap['attribution']}"
        # attribution_size=6)  # , zoom=15)
        cx.add_basemap(ax, crs="EPSG:25833",
                       source=basemap, attribution=attrib,)

        # ax.set_title('title')
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.margins(0)
        ax.tick_params(left=False, labelleft=False,
                       bottom=False, labelbottom=False)

        ax.axes.xaxis.set_visible(False)
        ax.axes.yaxis.set_visible(False)
        # plt.tight_layout()
        # fig.tight_layout()

        # workaround for Exception in Tkinter callback:
        fig.canvas.start_event_loop(sys.float_info.min)
        outfile = f"output/{timestamp}{name_extra}_{isovalue_name}.png"
    # %%
        fig.savefig(outfile, bbox_inches='tight')
        plt.close()
        print(f'Saved {outfile}')

        return True
    else:
        return False
    # %%


def plot_run_boundary5km():
    # %%
    from shapely.geometry import Polygon, mapping
    run = "run_boundary5km"
    ring = overlap.isocurve(5, overlap.GROTSUND_COORD)
    fig, ax = plt.subplots(dpi=250)  # figsize=(10, 10))

    ring = ring.set_crs('EPSG:4326')

    ring.to_crs('EPSG:25833', inplace=True)
    ring.geometry = [Polygon(mapping(x)['coordinates']) for x in ring.geometry]

    minx, miny, maxx, maxy = ring.geometry.total_bounds
    padding_m = (maxx-minx)/100*100*.15
    ax.set_xlim(minx - padding_m, maxx + padding_m)
    ax.set_ylim(miny - padding_m, maxy + padding_m)

    # Add scale-bar
    x, y, scale_len = maxx+padding_m-2500, miny - \
        padding_m+200, 2000  # arrowstyle='-'
    scale_rect = matplotlib.patches.Rectangle(
        (x, y), scale_len, 100, linewidth=0.5, edgecolor='k', facecolor='k')
    ax.add_patch(scale_rect)
    plt.text(x+scale_len/2, y+300, s='2 KM',
             fontsize=6, horizontalalignment='center')

    # Add release point

    # , color=None, edgecolor='k',linewidth = 2, )#facecolor=None)
    ring.boundary.plot(ax=ax, edgecolor='black')
    releasepoint = overlap.create_point(overlap.GROTSUND_COORD)
    # , markersize=150, color=None, edgecolor='k',linewidth = 2, facecolor=None)
    releasepoint.plot(ax=ax,  marker='x', color='black')

    basemap = cx.providers.CartoDB.Voyager
    #basemap = cx.providers.Stamen.Terrain
    cx.add_basemap(ax, crs="EPSG:25833", source=basemap,
                   attribution=f"Bakgrunnskart: {basemap.attribution}", attribution_size=6)

    # ax.set_title('title')
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False,
                   bottom=False, labelbottom=False)

    # plt.savefig('sample.png', bbox_inches="tight", pad_inches=0)

    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    plt.tight_layout()
    fig.tight_layout()
    # workaround for Exception in Tkinter callback
    fig.canvas.start_event_loop(sys.float_info.min)

    fig.savefig(f"{run}.png", bbox_inches='tight')
    print(f'Saved {run}.png')
    # %%


    # %%
if __name__ == '__main__':
    base5km = 'grotsund_arp_12h-100m_5km'
    base60km = 'grotsund_arp_12h-max'

    # Lag kart med sirkel for "run boundary"
    # plot_run_boundary5km()
    # plot_run_boundary65km()

    create_all(base5km)
    create_all(base60km)

    plot_CM(countermeasure='Matproduksjon')
    # plot_CM('iodine_child')
