import speasy
import pickle as pkl
import sys

parameter_id = sys.argv[1]
start_time = sys.argv[2]
stop_time = sys.argv[3]

p = speasy.get_data(parameter_id, start_time, stop_time)

if "/" in parameter_id:
    parameter_name = parameter_id.split("/")[1]
else:
    parameter_name = parameter_id
pkl.dump((p.time, p.data), open("{}_data.pkl".format(parameter_name), "wb"))
