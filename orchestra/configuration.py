"""Orchestra default configuration values
"""
import os, pwd

os.getlogin = lambda: pwd.getpwuid(os.getuid())[0]

orchestra_hostname = os.environ["ORCHESTRA_HOSTNAME"]

# Docker related config
docker_user = os.environ["ORCHESTRA_USER"] #os.getlogin()
docker_user_uid = os.environ["ORCHESTRA_UID"] #os.getuid()

# Postgresql
postgresql_user = os.environ["POSTGRESQL_USER"]
postgresql_password = os.environ["POSTGRESQL_PASSWORD"]
postgresql_host = os.environ["POSTGRESQL_HOSTNAME"]
postgresql_db = os.environ["POSTGRESQL_DB"]
postgresql_port = os.environ["POSTGRESQL_PORT"] # not used yet

# Redis
redis_host = os.environ["REDIS_HOSTNAME"]
redis_port = os.environ["REDIS_PORT"] # not used yet

# data directory
data_directory = "/var/lib/orchestra"

# task output directory
task_directory = os.path.join(data_directory, "task_outputs")
# archive directory
archive_directory = os.path.join(data_directory, "archives")
