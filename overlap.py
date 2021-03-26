
# %%

import geopandas as gpd
import shapely
import geopandas
from typing import NewType, TypeVar
from functools import lru_cache


KJELLER_COORD = (11.051946, 59.974542) # opposite of  lon/lat than google maps..
GROTSUND_COORD = (19.139001, 69.747223) # opposite of  lon/lat than google maps..
tromso_area = geopandas.read_file('kart/tromso2.shp') #broken?!

# %%

def get_area_max(area, dep_df):
    ov = geopandas.overlay(area, dep_df)
    if not ov.empty:
        # ov.plot()
        return ov.Value.max()
    else:
        print("No overlap")
        return 0


Isocurve = NewType('Isocurve', shapely.geometry.LinearRing)

def create_point(startingpoint: tuple):
    p = shapely.geometry.Point(([startingpoint[0], startingpoint[1]]))
    areas = gpd.GeoDataFrame(columns=['name', 'geometry'])
    areas.loc[0] = ("point", p)

    areas = areas.set_crs(epsg=4326)
    areas = areas.to_crs(epsg=25833)
    return areas

@lru_cache
def isocurve(distance_km, startingpoint: tuple) -> Isocurve:
    print(f"creating {distance_km} km isocurve")
    areas = create_point(startingpoint)

    areas.loc[1] = (
        distance_km, areas.loc[0].geometry.buffer(distance_km*1000))

    areas = areas.drop(0)
    areas = areas.set_crs(epsg=25833)
    areas = areas.to_crs(epsg=4326)
    areas.geometry = areas.exterior
    return areas


def get_isocurve_max(distance_km, startingpoint: tuple, depo_df):
    ring = geopandas.overlay(isocurve(distance_km, startingpoint), depo_df)
    return ring.Value.max()

# %%
if __name__ == "__main__":
    dep_shp =r"C:\Utvikling\Argos\BatchShpToTable\indata\20200616T190500Z\Shape\AnlopGrotsund_phase3_250m_202006161905_4800_grid_depos_bitmp_I-131.shp"
    dep = geopandas.read_file(dep_shp)

    matches = get_area_max(tromso_area, dep)
    # px = tromso_area.plot()
    # dep = geopandas.read_file(r"C:/Utvikling/Argos/batch/20201001T010000Z/Shape/grotsund_arp_12h-max_202010010100_3000_grid_depos_bitmp_I-131.shp")


    a=isocurve(10, GROTSUND_COORD)
    # %%
    # get_possible_matches(depo_df,match_area)
    # ring = get_area_max(dep, a)
    ring = geopandas.overlay(a, dep)

    ring.plot(column='Value')


    # %%
    ax = a.plot()
    dep.plot(ax=ax)
    tromso_area.plot(ax=ax)


# %%