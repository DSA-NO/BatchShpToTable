"""
Default colormaps to be used by DSA for ARGOS output
Based on https://plotly.com/python/builtin-colorscales/
See color ranges.xlsm
"""

toteff_rgb = {
    1.001: (255, 245, 240),
    5: (254, 224, 210),
    10: (252, 187, 161),
    20: (252, 146, 114),
    50: (239, 59, 44),
    100: (165, 15, 21),
    1000: (103, 0, 13)}


toteff = {k: [x/255 for x in v] for k, v in toteff_rgb.items()}

thyr_rgb = {
    10.001:  (196	, 230	, 195),
    50:  (150	, 210	, 164),
    100: (77	, 162	, 132),
    250: (54	, 135	, 122),
    1000: (29,	79,	96)
    }

thyr = {k: [x/255 for x in v] for k, v in thyr_rgb.items()}

if __name__ == '__main__':
    print(toteff)
