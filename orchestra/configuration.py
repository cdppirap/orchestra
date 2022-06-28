"""Orchestra default configuration values
"""
import os, pwd

os.getlogin = lambda: pwd.getpwuid(os.getuid())[0]

# docker related config
docker_user = os.getlogin()
docker_user_uid = os.getuid()

# module and task database
database = os.path.abspath("db.sqlite3")
module_info_table = "module_info"
task_info_table = "task_info"

# modules configuration , list of registered modules
module_file_path = "modules.pkl"

# virtual environement directory
environment_directory = "module_environments"

# task output directory
task_directory = "/var/lib/orchestra/task_outputs"

# REST configuration
rest_host = "0.0.0.0"#"127.0.0.1"
rest_port = 5000



