import sys
import os
from datetime import datetime, timedelta
import speasy as spz
import numpy as np

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("output_dir", type=str)
parser.add_argument("--parameter", type=str, default="imf")
parser.add_argument("--start", type=str, default="2000-01-01T00:00:00")
parser.add_argument("--stop", type=str, default="2000-01-02T00:00:00")
args = parser.parse_args()


def get_intervals(param, condition):
    intervals = []
    current_interval = []
    n = param.data.shape[0]
    for i in range(n):
        cond = condition(param.data[i,:])
        if cond:
            if len(current_interval)==0:
                # new interval
                current_interval.append(param.time[i])
                current_interval.append(param.time[i])
            else:
                current_interval[-1] = param.time[i]
        else:
            if len(current_interval)==2:
                intervals.append(current_interval)
                current_interval = []
    if len(current_interval)==2:
        intervals.append(current_interval)
    return intervals

td = timedelta(hours=1)

datefmt = "%Y-%m-%dT%H:%M:%S"

parameter = args.parameter
start = datetime.strptime(args.start, datefmt)
stop = datetime.strptime(args.stop, datefmt)

target_filename = os.path.join(args.output_dir, "out.cat")

p = spz.amda.get_data(parameter, start, stop)
intervals = get_intervals(p, lambda x: np.all(x<=0.))

with open(target_filename, "w") as f:
    for i in range(len(intervals)):
        interval = intervals[i]
        interval = [datetime.utcfromtimestamp(j) for j in interval]
        interval = [d.strftime(datefmt) for d in interval]
        f.write(" ".join(interval)+"\n")
