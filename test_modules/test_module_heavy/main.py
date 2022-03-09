import sys
import os
import numpy as np
from datetime import datetime, timedelta
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("output_dir", type=str)
parser.add_argument("--start", type=str, default="2000-01-01T00:00:00")
parser.add_argument("--stop", type=str, default="2000-01-02T00:00:00")
args = parser.parse_args()




target_filename = os.path.join(args.output_dir, "out.csv")
i=0
n=1000000

with open(target_filename, "w") as f:
    while i<n:
        f.write(str(np.random.random_sample(5).tolist())+"\n")
        i+=1


