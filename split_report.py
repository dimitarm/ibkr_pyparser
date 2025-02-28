import pandas as pd
import sys
from pathlib import Path
import argparse

def remove_empty_series(df:pd.DataFrame) -> pd.DataFrame:
    non_empty_series = []
    for column in df.columns:
        if len(df[column].unique()) > 1:
            non_empty_series.append(column)
    return df[non_empty_series]

def main():
    parser = argparse.ArgumentParser(
                        prog='split_report',
                        description='IBKR report splitter')
    parser.add_argument('report_path')           
    parser.add_argument('-o', '--output_path', default='.')
    parser.add_argument('-v', '--verbose')
    args = parser.parse_args()

    main_report = pd.read_csv(args.report_path, quotechar = '"', header=None, names=range(40))
    subreports = dict()

    for header in main_report[0].unique():
        subreports[header] = main_report[main_report[0] == header]

    stem = Path(args.report_path).stem
    if args.output_path[-1] != '/':
        output_path = args.output_path + "/"
    else:
        output_path = args.output_path
    for name,df in subreports.items():
        output_file = output_path + stem + "_" + name.replace("/", "_").replace(" ", "_") + ".csv"
        print ("Saving " + name + " to " + output_file)
        df = remove_empty_series(df)
        df.to_csv(output_file, header = False, index = False, mode = 'w')


if __name__ == '__main__':
    sys.exit(main())  