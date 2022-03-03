import sys
import os
from datetime import datetime, timedelta
import numpy as np

td = timedelta(minutes=1)

datefmt = "%Y-%m-%dT%H:%M:%S"

output_dir = sys.argv[1]
#parameter = sys.argv[2]
start = datetime.strptime(sys.argv[2], datefmt)
stop = datetime.strptime(sys.argv[3], datefmt)

target_filename = os.path.join(output_dir, "out.csv")
curr_dt = start
with open(target_filename, "w") as f:
    while curr_dt < stop:
        line = "{} {}\n".format(curr_dt.strftime(datefmt), np.random.random_sample())
        f.write(line)
        curr_dt += td


