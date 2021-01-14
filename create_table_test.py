import create_table
import sys

def get_shp_max_dummy(txtfile):
    """
    DUMMY
    """
    try:
        with open(str(txtfile)+".txt") as ifile:
            value =  ifile.readlines()[0].strip()
    except:
        value = 1337
    return {'top10': value, 'max': value}


create_table.get_gdf_max = get_shp_max_dummy

sys.argv.append("indata")
print(sys.argv)
create_table.main()
