import speasy as spz
import pandas as pd
import sys
import os

output_dir = sys.argv[1]
parameter = sys.argv[2]
start = sys.argv[3]
stop = sys.argv[4]

p = spz.get_data("amda/{}".format(parameter), start, stop)
target_filename = os.path.join(output_dir, "output.csv")

df = pd.DataFrame(data=p.data, index=p.time)
df.to_csv(target_filename)
