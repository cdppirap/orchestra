import sys
import os

target_dir = sys.argv[1]
start = sys.argv[2]
stop = sys.argv[3]

input_file = "model_regions_plasmas_mms_2019.txt"
output_file = os.path.join(target_dir, "breuillard.cat")
os.system("cp {} {}".format(input_file, output_file))
