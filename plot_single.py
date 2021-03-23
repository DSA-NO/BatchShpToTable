"""
Script that locates runs with max values in at specificas areas/distances and plots on a map.
"""
# %%
import geopandas as gpd
import pandas as pd



# %%
maxvals: pd.DataFrame = pd.read_excel('output/Max_values_grotsund_arp_12h-100m_5km.xlsx', header=[0,1,2,3,4], index_col=[0,1])
df=maxvals.transpose()

# Get max value Total effective dose [Sv] at 48 h:
max48=df.loc[("Total effective dose [Sv]", 48, )].max().max() 
# %%
# Find where max48 is:
maxrow = df[df.eq(max48).any(1)].transpose()
maxrow.index = maxrow.index.droplevel()
maxrow.idxmax()
# %%
# Read the max run
localmax= r"E:\ArgosBatch\grotsund_arp_12h-100m_5km.\20200715T190000Z\Shape\grotsund_arp_12h-100m_5km_202007151900_4800_grid_toteffout_bitmp_Adults_Total.shp"

gdf = gpd.read_file(localmax)
# %%


toteff48 = pd.read_pickle("grotsund_arp_12h-max4800_grid_toteffout_bitmp_Adults_Total__full.pkl.bz2")

# %%
