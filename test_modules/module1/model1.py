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

parameter_id = args.parameter
if not parameter_id.startswith("amda/"):
    parameter_id=os.path.join("amda", parameter_id)
p = spz.get_data(parameter_id, args.start, args.stop)

target_filename = os.path.join(args.output_dir, "output.csv")

if p is None:
    os.system("touch {}".format(target_filename))
    exit()
df = pd.DataFrame(data=p.data, index=p.time)
df.to_csv(target_filename)
