"""
Default colormaps to be used by DSA for ARGOS output 
Based on https://plotly.com/python/builtin-colorscales/
See color ranges.xlsm
"""

toteff_rgb = {\
    20: (252,146,114),
    50: (239,59,44),
    100: (165,15,21),
    1000:(103,0,13)}


toteff = {k/1000:[x/255 for x in v] for k,v in toteff_rgb.items()} 

if __name__ == '__main__':
    print(toteff)