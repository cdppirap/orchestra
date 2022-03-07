import docker
import os
from io import BytesIO

from orchestra.context import PythonRequirements, PythonContext

class ContextManager:
    def __init__(self):
        self.client = None
    def open_client(self):
        self.client = docker.from_env()
    def close_client(self):
        self.client.close()
    def build(self, context):
        # create a temporary directory in which to store the dockerfile and other resources
        import tempfile
        parent_dir = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            # change the current working directory
            os.chdir(tmpdir)
            # dockerfile creationg
            dockerfile = context.to_dockerfile()
            with open("dockerfile","wb") as f:
                f.write(dockerfile.read())
                dockerfile.close()

            # move files to build context
            for f in context.files:
                os.system("cp -r {} .".format(f))
            
            # build the image
            self.open_client()
            image,_ = self.client.images.build(path=".")
            self.close_client()

            # move back to parent directory
            os.chdir(parent_dir)
            return image

    def run(self, context, command, output_dir):
        self.open_client()
        # create the mount
        #m = docker.types.Mount(target=output_dir, source="output")
        m = docker.types.Mount(target="/output", source=os.path.abspath(output_dir), type="bind")
        logs = self.client.containers.run(context , command,  mounts=[m], auto_remove=True, user=os.getuid())
        self.close_client()
        return logs
    def get(self, context_id):
        print("Get context id={}".format(context_id))
    def delete(self, context):
        with docker.from_env() as client:
            client.images.remove(image=context.id)
        print("Delete context id={}".format(context.id))
    def context_exists(self, context_id):
        self.open_client()
        a=context_id in [img.id for img in self.client.images.list()]
        self.close_client()
        return a

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

