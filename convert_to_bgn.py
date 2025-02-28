import pandas as pd
import sys
from utils.rates_parser import rates_df
from os import path
from pathlib import Path
import argparse
from datetime import datetime, timedelta
from math import nan

def get_rate_for_missing_day(rates:pd.DataFrame, column:str, dt:datetime) -> float:
    initdate = dt
    oneday = timedelta(days=1)
    for i in range(0,10):
        dt = dt + oneday
        try:
            rate = rates[column][dt]
            print("Rate for currency {0} for date {1} found at {2}".format(column, initdate, dt))
            return rate
        except KeyError:
            pass
    print("No value for currency {0} for date {1}".format(column, initdate))
    sys.exit(-1)
    


def main(file:str, rates:pd.DataFrame, col_value:str, col_cur:str, col_date:str, output_path:str):
    df = pd.read_csv(file)
    df.insert(loc = df.shape[1], column = col_value + "_bgn", value = pd.NA)
    col_bgn = df.shape[1] - 1

    for idx in range(df.shape[0]):
        if(isinstance(df.iloc[idx][col_date], str)):
            row = df.iloc[idx]
            try:
                dt = datetime.strptime(row[col_date][0:10], "%Y-%m-%d") #2024-01-09, 03:00:12
                try:
                    day_rate = rates[row[col_cur]][dt]
                    if pd.isna(day_rate):
                        day_rate = get_rate_for_missing_day(rates, row[col_cur], dt)
                except KeyError:
                    day_rate = get_rate_for_missing_day(rates, row[col_cur], dt)

                bgvalue = day_rate * float(row[col_value])
                df.iloc[idx, col_bgn] = bgvalue
            except ValueError:
                df.iloc[idx, col_bgn] = nan
    print("Saving in " + output_path)
    df.to_csv(output_path, mode = 'w')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                        prog='convert_to_bgn',
                        description='Converts a column to BGN')
    parser.add_argument('csv_report', help="report to be converted, could be glob file mask")
    parser.add_argument('-c','--column', help="column to be converted, can be name or integer/index", default = "Realized P/L")
    parser.add_argument('-t', '--currency', help="column which specifies the currency which is to be converted to BGN, can be name or integer", default="Currency")
    parser.add_argument('-d', '--date', help="column which specifies the date which is to be used when converting the value to BGN, can be name or integer", default="Date/Time")
    parser.add_argument('-r', '--rates', help="BGN rates file or folder", required=True)
    parser.add_argument('-o', '--output', help="Output path folder, if not specified stores output in same folder as input file", required=False)
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    df = rates_df(args.rates)

    tobeprocessed = {}
    for file in sorted(Path('.').glob(args.csv_report)):
        path = Path(file)
        if args.output is not None:
            to_besaved = args.output + "/" + str(path.stem) + "_to_bgn.csv"
        else:
            to_besaved = str(path.parent) + "/" + str(path.stem) + "_to_bgn.csv"
        tobeprocessed[file] = to_besaved

    for file, output in tobeprocessed.items():
        print(f"{file} => {output}")
    print("Press RETURN to proceed or CTRL-C to abort")
    input()

    for file, output in tobeprocessed.items():
        main(file, df, args.column, args.currency, args.date, output)

