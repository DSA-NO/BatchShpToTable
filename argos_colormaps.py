"""
Default colormaps to be used by DSA for ARGOS output
Based on https://plotly.com/python/builtin-colorscales/
See color ranges.xlsm
"""

# mSv
toteff_rgb = {
    1.001: (255, 245, 240),
    5: (254, 224, 210),
    10: (252, 187, 161),
    20: (252, 146, 114),
    50: (239, 59, 44),
    100: (165, 15, 21),
    1000: (103, 0, 13)}

toteff_hex = {
    1: '#fcfdbf',
    5: '#feca8d',
    10: '#fd9668',
    20: '#cd4071',
    50: '#721f81',
    100: '#440f76',
    1000: '#000004'}


toteff = toteff_hex
toteff_modifier = 1000

# toteff = {k: [x/255 for x in v] for k, v in toteff_rgb.items()}

# mSv
thyr_rgb = {
    10:  (196	, 230	, 195),
    50:  (150	, 210	, 164),
    100: (77	, 162	, 132),
    250: (54	, 135	, 122),
    1000: (29,	79,	96)
    }

thyr = {k: [x/255 for x in v] for k, v in thyr_rgb.items()}
thyr_modifier = 1000

#kBq
depo = {k:k for k in [1, 10, 100, 1000, 10000 ]} #used color from magma_r
depo_modifier = 1/1000

# Tiltak reinsdyr
rein = {k:k for k in [2000, 2000, 2000, 2000, 2000]} #used color from magma_r
rein_modifier = 1


if __name__ == '__main__':
    print(toteff)
