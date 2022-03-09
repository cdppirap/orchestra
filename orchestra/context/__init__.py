import os
from io import BytesIO

import orchestra.configuration as config

class PythonRequirements:
    def __init__(self, requirements=[], filename=None):
        self.requirements = requirements
        if filename is not None:
            self += PythonRequirements.from_file(filename=filename)
    @staticmethod
    def from_file(filename=None):
        if not os.path.exists(filename):
            return PythonRequirements()
        with open(filename,"r") as f:
            return PythonRequirements(requirements=[l for l in f.read().split("\n") if len(l)])
    def __len__(self):
        return len(self.requirements)
    def __str__(self):
        return "PythonRequirements ({})".format(",".join(self.requirements))
    def pip_str(self):
        return " ".join(self.requirements)

class PythonContext:
    def __init__(self, requirements=[], files=[], python_version="3.6"):
        self.python_version = python_version
        self.requirements=requirements
        self.files = files
    def __str__(self):
        return "PythonContext (version={}, requirements={}, files={})".format(self.python_version, self.requirements, self.files)
    def to_dockerfile(self):
        # all files must be moved to a temporary directory within the build context
        content = """FROM python:{}-slim-buster
RUN useradd --create-home --no-log-init --shell /bin/bash --uid {} {}
USER {}
WORKDIR /home/{}""".format(self.python_version, config.docker_user_uid, config.docker_user,
            config.docker_user, config.docker_user)
        # create a user
        if len(self.requirements):
            content += "\n"+"RUN pip install {}".format(self.pip_str())
        if len(self.files):
            content += "\n"+"COPY {} /home/{}/".format(self.file_str(), config.docker_user)
        #print("Content ")
        #print(content)
        #print()
        return BytesIO(bytearray(content.encode()))
    def pip_str(self):
        return self.requirements.pip_str()
    def file_str(self):
        r=" ".join([os.path.basename(f) for f in self.files])
        return r



