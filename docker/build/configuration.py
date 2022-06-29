"""Orchestra default configuration values
"""
import os

# docker related config
docker_user = 'orchestra'
docker_user_uid = os.getenv('ORCHESTRA_UID')

# module and task database
database = os.path.abspath("/orchestra_data/db.sqlite3")
module_info_table = "module_info"
task_info_table = "task_info"

# modules configuration , list of registered modules
module_file_path = "/orchestra_data/modules.pkl"

# virtual environement directory
environment_directory = "/orchestra_data/module_environments"

# task output directory
task_directory = "/orchestra_data/task_outputs"

# REST configuration
rest_host = "0.0.0.0"
rest_port = 5000
