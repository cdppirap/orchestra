import docker
import os
from io import BytesIO
import tempfile

from orchestra.context import PythonRequirements, PythonContext

class ContextManager:
    """Interface for managing docker images and containers
    """
    def __init__(self):
        """Initialize manager
        """
        self.client = None
    def open_client(self):
        """Open connection to docker daemon
        """
        self.client = docker.from_env()
    def close_client(self):
        """Close connection to docker daemon
        """
        self.client.close()
    def build(self, context, tag="orchestra:latest"):
        """Build an image for a given context
        """
        # create a temporary directory in which to store the dockerfile and other resources
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
            try:
                image,logs = self.client.images.build(path=".", tag=tag, nocache=True)
            except Exception as e:
                print(e)
                print(logs)

            self.close_client()

            # move back to parent directory
            os.chdir(parent_dir)
            return image

    def run(self, context, command, output_dir):
        """Execute the module in its container
        """
        self.open_client()
        # create the mount
        m = docker.types.Mount(target="/output", source=os.path.abspath(output_dir), type="bind")
        logs = None
        try:
            logs = self.client.containers.run(context , command,  mounts=[m], 
                auto_remove=False, 
                #user=os.getuid(),
                detach=False)
                #cpu_period=100000,
                #cpu_quota=100000)
            #print("RES", logs.wait())
            #logs.remove()
        except Exception as e:
            print("3EEEEEEEEEEEEEEEEEEEEEEE", e)
        self.close_client()
        return logs
    def remove(self, context):
        """Delete a context
        """
        self.open_client()
        try:
            self.client.images.remove(image=context, force=True)
        except Exception as e:
            pass
        self.close_client()
    def context_exists(self, context_id):
        """Check that context exists
        """
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

