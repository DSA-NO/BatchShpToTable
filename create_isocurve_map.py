# %%
import pandas as pd


# Keep only with distance
# df = df[[x for x in df.columns if x[-1].endswith('km')]]
from create_table import DISTANCES
import overlap
import matplotlib as plt


import contextily as cx


# %%
# def main():

pkl = "grotsund_arp_12h-max.pkl"
df = pd.read_pickle(pkl)
m = df.max()
values = m.loc[("Deposition [Bq/m2]", 48, slice(None), '', 'Cs-137 ')]


fig, ax = plt.subplots(dpi=200)  # figsize=(10, 10))

minx = ds2.longitude.min().values
maxx = ds2.longitude.max().values
miny = ds2.latitude.min().values
maxy = ds2.latitude.max().values


# gpd.read_file(gpd.datasets.get_path('naturalearth_lowres')).plot(
#     ax=ax, color='grey', label=ds2.attrs['title']) #replaced by basemap from contextily

ds2.where(ds2 > 0).plot(
    ax=ax, add_colorbar=False, robust=True, cmap=plt.cm.Wistia, alpha=0.3)

basemap = cx.providers.CartoDB.Voyager
# basemap = cx.providers.Stamen.Terrain
cx.add_basemap(ax, crs="EPSG:4326", source=basemap,
               attribution=f"Bakgrunnskart: {basemap.attribution}")

# ax.set_xlim(minx - 1, maxx + 1)
# ax.set_ylim(miny - 1, maxy + 1)
# ax.set_title(ds2.attrs['title'])
# ax.set_xlabel('')
# ax.set_ylabel('')

# ax.axes.xaxis.set_visible(False)
# ax.axes.yaxis.set_visible(False)
plt.tight_layout()
# fig.savefig(f"{ds2.attrs['title']}.png")

fig.show()


if __name__ == "__main__":
    main()
# m.loc[("Deposition [Bq/m2]",48,slice(None), slice(None), 'Cs-137 ')]
