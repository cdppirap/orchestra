import speasy
import pandas as pd
import sys
import os

output_dir = sys.argv[1]
parameter_id = sys.argv[2]
start_time = sys.argv[3]
stop_time = sys.argv[4]

p = speasy.get_data("amda/"+parameter_id, start_time, stop_time)

output_filename = os.path.join(output_dir, "output.csv")
df = p.to_dataframe()
df.to_csv(output_filename)
