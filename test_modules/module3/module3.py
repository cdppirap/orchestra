import speasy as spz
import pandas as pd
import sys
import os
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("output_dir", type=str)
parser.add_argument("--parameter", type=str, default="imf")
parser.add_argument("--start", type=str, default="2000-01-01T00:00:00")
parser.add_argument("--stop", type=str, default="2000-01-02T00:00:00")
args = parser.parse_args()


output_dir = args.output_dir
parameter =args.parameter
start = args.start
stop = args.stop

p = spz.get_data("amda/{}".format(parameter), start, stop)
target_filename = os.path.join(output_dir, "output.csv")

df = pd.DataFrame(data=p.data, index=p.time)
df.to_csv(target_filename)
