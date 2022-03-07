import os
import orchestra.configuration as config

def get_rest_base_url():
    return "http://{}:{}/".format(config.rest_host, config.rest_port)
# endpoint urls
def get_rest_modules_url():
    return os.path.join(get_rest_base_url(),"modules")
def get_rest_module_info_url(module_id):
    return os.path.join(get_rest_base_url(),"modules/{}".format(module_id))
def _module_run_parameter_string(**kwargs):
    return "parameter={}&start={}&stop={}".format(kwargs["parameter"], kwargs["start"], kwargs["stop"])
def get_rest_module_run_url(module_id, **kwargs):
    s = _module_run_parameter_string(**kwargs)
    return os.path.join(get_rest_base_url(),"modules/{}/run?{}".format(module_id, s))
def get_rest_tasks_url():
    return os.path.join(get_rest_base_url(),"tasks")
def get_rest_task_info_url(task_id):
    return os.path.join(get_rest_base_url(),"tasks/{}".format(task_id))
def get_rest_task_output_url(task_id):
    return os.path.join(get_rest_base_url(),"tasks/{}/output".format(task_id))


