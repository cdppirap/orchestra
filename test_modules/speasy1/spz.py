import speasy
import pandas as pd
import sys
import os

import argparse

# parse arguments
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=str)
    parser.add_argument("--start", type=str, default="2000-01-01T00:00:00")
    parser.add_argument("--stop", type=str, default="2000-01-02T00:00:00")
    parser.add_argument("--parameter", type=str, default="imf")
    return parser.parse_args()

args=parse_args()

p = speasy.get_data("amda/"+args.parameter, args.start, args.stop)

output_filename = os.path.join(args.output_dir, "output.csv")
df = p.to_dataframe()
df.to_csv(output_filename)
