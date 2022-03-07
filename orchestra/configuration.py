"""Orchestra default configuration values
"""
import os

# module database
module_database = os.path.abspath("db.sqlite3")
module_info_table = "module_info"

# modules configuration , list of registered modules
module_file_path = "modules.pkl"

# virtual environement directory
environment_directory = "module_environments"

# task output directory
task_directory = "task_outputs"

# REST configuration
rest_host = "127.0.0.1"
rest_port = 5000



