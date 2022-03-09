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

output_dir = args.output_dir
parameter = args.parameter
start = args.start
stop = args.stop

target_filename = os.path.join(output_dir, "output.csv")
target_filename_2 = os.path.join(output_dir, "annexe.csv")

with open(target_filename, "w") as f:
    f.write("parameter : {}\n".format(parameter))
    f.write("start     : {}\n".format(start))
    f.write("stop      : {}\n".format(stop))

with open(target_filename_2, "w") as f:
    f.write("annexe")
