import sys
import os

output_dir = sys.argv[1]
parameter = sys.argv[2]
start = sys.argv[3]
stop = sys.argv[4]

target_filename = os.path.join(output_dir, "output.csv")
with open(target_filename, "w") as f:
    f.write("hello")


