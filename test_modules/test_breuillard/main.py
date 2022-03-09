import sys
import os

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("output_dir", type=str)
parser.add_argument("--start", type=str, default="2000-01-01T00:00:00")
parser.add_argument("--stop", type=str, default="2000-01-02T00:00:00")

args = parser.parse_args()

input_file = "model_regions_plasmas_mms_2019.txt"
output_file = os.path.join(args.output_dir, "breuillard.cat")
os.system("cp {} {}".format(input_file, output_file))
