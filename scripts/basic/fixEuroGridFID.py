import pandas as pd
import sys
sys.path.append('./')
from config.rom import years_list_hist

def fixEuroGrid(input, output):
    df = pd.read_csv(input)
    df['eurogrid']= df['lon'].astype(int).astype(str) + 'N' + df['lat'].astype(int).astype(str) + 'E'
    df=df.drop(columns=['Unnamed: 0'])
    df.to_csv(output)

for year in years_list_hist:
    input = '/home/ubuntu/MeasuringSegregation/Rome/data/CSV/{}.csv'.format(year)
    output = '/home/ubuntu/MeasuringSegregation/Rome/data/CSV_hist/{}.csv'.format(year)
    fixEuroGrid(input, output)