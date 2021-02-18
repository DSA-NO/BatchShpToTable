
import pandas as pd


pkl = "Shape.pkl"
df = pd.read_pickle(pkl)

# Keep only with distance
df = df[[x for x in df.columns if x[-1].endswith('km')]].to_excel("km.xlsx")
