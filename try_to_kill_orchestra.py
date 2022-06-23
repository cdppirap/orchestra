from multiprocessing import Process
import urllib.request
import json
import time

module_id = 2
run_url = f"http://orchestra:5000/modules/{module_id}/run"
task_url = "http://orchestra:5000/tasks/{}"

def request_run():
    t0 = time.time()
    task_id = None
    with urllib.request.urlopen(run_url) as f:
        data = json.loads(f.read())
        task_id = data["task"]

    if task_id:
        # wait for task to end
        while True:
            with urllib.request.urlopen(task_url.format(task_id)) as f:
                task_status = json.loads(f.read())["status"]
                if task_status == "done":
                    break
                time.sleep(5)
    return time.time() - t0

n_process = 100

processes = [Process(target=request_run) for _ in range(n_process)]
# start all the processes
print("Starting processes")
s=[p.start() for p in processes]
#for process in processes:
#    process.start()
#    time.sleep(.1)
print("done")

while True:
    flags = [p.is_alive() for p in processes]
    n_done = sum([int(f) for f in flags])
    print(f"Finished {n_done}/{n_process}")
    if n_done == 0:
        break
    time.sleep(5)


print("All done")
