import sys
import os
from datetime import datetime, timedelta

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("output_dir", type=str)
parser.add_argument("--parameter", type=str, default="imf")
parser.add_argument("--start", type=str, default="2000-01-01T00:00:00")
parser.add_argument("--stop", type=str, default="2000-01-02T00:00:00")
args = parser.parse_args()


td = timedelta(hours=1)

datefmt = "%Y-%m-%dT%H:%M:%S"

parameter = args.parameter
start = datetime.strptime(args.start, datefmt)
stop = datetime.strptime(args.stop, datefmt)

target_filename = os.path.join(args.output_dir, "out.cat")
curr_dt = start
with open(target_filename, "w") as f:
    while curr_dt < stop:
        line = "{} {} 1\n".format(curr_dt.strftime(datefmt), (curr_dt+td).strftime(datefmt))
        f.write(line)
        curr_dt += 2*td


