import sys
import os
from datetime import datetime, timedelta

td = timedelta(hours=1)

datefmt = "%Y-%m-%dT%H:%M:%S"

output_dir = sys.argv[1]
#parameter = sys.argv[2]
start = datetime.strptime(sys.argv[2], datefmt)
stop = datetime.strptime(sys.argv[3], datefmt)

target_filename = os.path.join(output_dir, "out.tt")
curr_dt = start
with open(target_filename, "w") as f:
    while curr_dt < stop:
        line = "{} {}\n".format(curr_dt.strftime(datefmt), (curr_dt+td).strftime(datefmt))
        f.write(line)
        curr_dt += 2*td


