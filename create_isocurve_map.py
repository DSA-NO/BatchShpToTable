# %%
import pandas as pd
import overlap
import matplotlib.pyplot as plt
import contextily as cx
import shapely
from shapely.geometry import Polygon, mapping
# %%
def main():
    pass
pkl = "grotsund_arp_12h-max.pkl"
df = pd.read_pickle(pkl)
m = df.max()
values = m.loc[("Deposition [Bq/m2]", 48, slice(None), '', 'Cs-137 ')]
distances = [float(x.strip(" km")) for x in values.reset_index().Distance]



circs = []
for d,dist in enumerate(distances):
    ring = overlap.isocurve(dist, overlap.GROTSUND_COORD)
    # ring.geometry = shapely.geometry.Polygon(ring.geometry.iloc[0])
    ring.geometry = [Polygon(mapping(x)['coordinates']) for x in ring.geometry]
    circs.append(ring)
    
gdf = pd.concat(circs) 
gdf['value'] = values.values
gdf.sort_values('name', inplace=True, ascending=False)


# %%
fig, ax = plt.subplots(dpi=250)  # figsize=(10, 10))


gdf.geometry = gdf.geometry.to_crs('EPSG:25833')

gdf.boundary.plot(ax=ax)  # column='value', alpha=.3)#, cmap=plt.cm.Wistia)
# overlap.tromso_area.to_crs('EPSG:25833').plot(ax=ax)

basemap = cx.providers.CartoDB.Voyager
# basemap = cx.providers.Stamen.Terrain
cx.add_basemap(ax, crs="EPSG:25833", source=basemap,
               attribution=f"Bakgrunnskart: {basemap.attribution}")
minx, miny, maxx, maxy = gdf.geometry.total_bounds
ax.set_xlim(minx - 3000, maxx + 3000)
ax.set_ylim(miny - 3000, maxy + 3000)
# ax.set_title(ds2.attrs['title'])
ax.set_xlabel('')
ax.set_ylabel('')



# lovande..
i = 0
for x, y, label in zip((gdf.geometry.bounds['maxx']+gdf.geometry.bounds['minx'])/2, gdf.geometry.bounds['maxy'], gdf.name):
    ax.annotate(label, xy=(x, y),  xytext=(i, 4),  # 3 points vertical offset
                textcoords="offset points",
                ha='center', va='center',
                arrowprops=dict(facecolor='black', lw=1, arrowstyle='-'))
    i += 15



ax.axes.xaxis.set_visible(False)
ax.axes.yaxis.set_visible(False)
plt.tight_layout()
fig.savefig(f"{pkl}.png")
fig.savefig(f"/mnt/hgfs/Utvikling/Argos/BatchShpToTable/{pkl}.png")

# fig.show()

# %%
if __name__ == "__main__":
    main()


# %%
