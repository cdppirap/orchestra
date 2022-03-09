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
    parser.add_argument("--a", type=int, default=0)
    parser.add_argument("--b", type=float, default=.5)
    parser.add_argument("--c", type=str, default="abc")
    return parser.parse_args()

args=parse_args()

output_dir = args.output_dir
parameter = args.parameter
start = args.start
stop = args.stop

target_filename = os.path.join(output_dir, "output.csv")
with open(target_filename, "w") as f:
    f.write("Arguments\n")
    f.write("parameter : {}\n".format(parameter))
    f.write("start     : {}\n".format(start))
    f.write("stop      : {}\n".format(stop))
    f.write("Hyper-parameters\n")
    f.write("a         : {}\n".format(args.a))
    f.write("b         : {}\n".format(args.b))
    f.write("c         : {}\n".format(args.c))
