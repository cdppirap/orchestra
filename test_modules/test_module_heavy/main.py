import sys
import os
import numpy as np
from datetime import datetime, timedelta


output_dir = sys.argv[1]

target_filename = os.path.join(output_dir, "out.csv")
i=0
n=1000000

with open(target_filename, "w") as f:
    while i<n:
        f.write(str(np.random.random_sample(5).tolist())+"\n")
        i+=1


