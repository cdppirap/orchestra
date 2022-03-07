import docker
import os
from io import BytesIO

from orchestra.context import PythonRequirements, PythonContext

class ContextManager:
    def __init__(self):
        self.client = docker.from_env()
    def build(self, context):
        # dockerfile 
        dockerfile = context.to_dockerfile()
        with open("dockerfile","wb") as f:
            f.write(dockerfile.read())
        # move files to build context
        fs = []
        for f in context.files:
            os.system("cp -r {} .".format(f))
            fs.append(os.path.basename(f))
        image,_ = self.client.images.build(path=".")
        for f in fs:
            os.system("rm -rf {}".format(f))
        # remove dockerfile
        os.system("rm -rf dockerfile")
        return image

    def run(self, context, command):
        #print("Run in context {} : {}".format(context, cmd))
        return self.client.containers.run(context , command, auto_remove=True)
    def get(self, context_id):
        print("Get context id={}".format(context_id))
    def delete(self, context):
        self.client.images.remove(image=context.id)
        print("Delete context id={}".format(context.id))

if __name__=="__main__":
    # create a context for testing
    requirements = PythonRequirements(requirements=["numpy","pandas"])
    context = PythonContext(requirements=requirements)

    # build a context
    cmanager = ContextManager()
    context = cmanager.build(context)
    print("Context ID : {}".format(context.id))

    # run a command
    cmd = "python -c \'import numpy as np\nprint(np.__version__)\'"
    cmd_output = cmanager.run(context, cmd)

    print("Command output : {}".format(cmd_output.decode("utf-8")))

    # remove context
    cmanager.delete(context)

