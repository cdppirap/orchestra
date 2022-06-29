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
    def __getitem__(self, i):
        return self.requirements[i]

class PythonContext:
    def __init__(self, requirements=[], files=[], python_version="3.6", post_process=[]):
        self.python_version = python_version
        self.requirements=requirements
        self.files = files
        self.post_process = post_process
    def __str__(self):
        return "PythonContext (version={}, requirements={}, files={})".format(self.python_version, self.requirements, self.files)
    def to_dockerfile(self, as_string=False):
        # all files must be moved to a temporary directory within the build context
        content = """FROM python:{}-slim-buster
RUN useradd --create-home --no-log-init --shell /bin/bash --uid {} {}""".format(self.python_version,
                                               config.docker_user_uid,
                                               config.docker_user)
        # upgrade pip to latest version
        content += "\nRUN pip install --upgrade pip"
        # install requirements if any
        if len(self.requirements):
            content += "\nADD requirements.txt requirements.txt"
            content += "\nRUN pip install -r requirements.txt"

        # login as orchestra user
        content += f"\nUSER {config.docker_user}"
        content += f"\nWORKDIR /home/{config.docker_user}"

        # move files
        if len(self.files):
            for f in self.files:
                content += "\n"+"ADD --chown={}:{} {} {}".format(config.docker_user, 
                        config.docker_user,
                        os.path.basename(f),
                        os.path.basename(f))
        #if len(self.requirements):
        #    content += "\nRUN pip install --upgrade pip"
        #    content += "\nRUN pip install --user -r requirements.txt"
        #    #content += "\nRUN python -m pip install --upgrade pip"
        #    #content += "\nRUN /usr/local/bin/python -m pip install --upgrade pip"
        #    #content += "\nRUN python -m pip install -r requirements.txt"

        if len(self.post_process):
            for p in self.post_process:
                content += "\n"+p
        if as_string:
            return content
        return BytesIO(bytearray(content.encode()))
    def pip_str(self):
        return self.requirements.pip_str()
    def file_str(self):
        r=" ".join([os.path.basename(f) for f in self.files])
        return r



