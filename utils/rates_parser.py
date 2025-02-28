import pandas as pd
import numpy as np
from datetime import date, datetime
import sys
from pathlib import Path

def read_rate_data(file:str, df:pd.DataFrame) -> pd.DataFrame:
    rates_df = pd.read_csv(file, skiprows = 2, date_format="%d.%m.%Y", header=None, index_col=0)
    for dt in rates_df.index:
        pos = 1
        row = rates_df.loc[dt]
        while(pos < len(row)):
            currency = row[pos].strip()
            pos += 1
            divisor = row[pos]
            pos += 1
            count = row[pos]
            bgn_rate = count/divisor
            #insert new currency if missing
            if currency not in df.columns: 
                df.insert(loc = len(df.columns), column=currency, value=np.nan, allow_duplicates=False)
            
            if dt not in df.index or pd.isna(df.loc[dt, currency]) or pd.isnull(df.loc[dt, currency]):
                df.loc[dt, currency] = bgn_rate
            else:
                raise Exception("There is present value for: " + dt + " row: " + row + " new value: " + currency + " " + bgn_rate)
            pos += 2 #skip last value
    return df

def rates_df(loc) -> pd.DataFrame:
    files = []
    if type(loc) is list or type(loc) is tuple:
        files = loc
    elif Path(loc).is_dir():
        files.extend(Path(loc).iterdir())
    else:
        files.append(loc)

    #create empty initial data frame
    df = pd.DataFrame(dtype = float)
    for fl in files:
        read_rate_data(fl, df)
    df.insert(loc = len(df.columns), column='EUR', value=np.nan, allow_duplicates=False)
    df['EUR'] = 1.95583
    return df

def main():
    files = "rates"
    print(rates_df(files).sort_index())

if __name__ == '__main__':
    sys.exit(main())  
