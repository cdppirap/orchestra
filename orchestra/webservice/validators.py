import json
from wtforms import validators
from .models import Module

class ModuleArchiveValidator(object):
    def __init__(self, extentions=[".zip"], message=None):
        self.extensions = extentions
        if not message:
            message = f"Input file must be one of the following type : {self.extensions}."
        self.message = message
    def __call__(self, form, field):
        extension = os.path.splitext(field.data.filename)[1]
        if not extension in self.extensions:
            raise validators.ValidationError(self.message+f" Got ({extension}).")

class OneOrTheOther(object):
    def __init__(self, fieldnames):
        self.fieldnames=fieldnames
    def __call__(self, form, field):
        fields = [form[f] for f in self.fieldnames]
        has_data = []
        for field in fields:
            if isinstance(field.data, str):
                has_data.append(len(field.data)>0)
            if isinstance(field.data, werkzeug.datastructures.FileStorage):
                has_data.append(len(field.data.filename)>0)
        if sum(has_data)!=1:
            raise validators.ValidationError("Please provide either a Github repository or an archive.")

def find_files(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            yield os.path.join(root, name)


class ModuleUniqueNameValidator(object):
    def __init__(self):
        self.message = "Module with name \"{}\" already exists."
    def __call__(self, form, field):
        # target filename 
        if len(field.data.filename)==0:
            return
        target_filename = os.path.join(current_app.instance_path, "archive", secure_filename(field.data.filename))

        # check file type
        extensions = [".zip"]
        extension = os.path.splitext(target_filename)[1]
        if not extension in extensions:
            message = f"Input file must be one of the following type : {extensions}."
            raise validators.ValidationError(message+f" Got ({extension}).")

        # save the archive
        if not os.path.exists(target_filename):
            field.data.save(target_filename)
        else:
            suffix = f"_{uuid.uuid4().hex[:4].upper()}"
            splitt = os.path.splitext(target_filename)
            while os.path.exists(splitt[0] + suffix + splitt[1]):
                suffix = f"_{uuid.uuid4().hex[:4].upper()}"
            target_filename = splitt[0] + suffix + splitt[1]
            # update filename
            field.data.filename = os.path.basename(target_filename)

            # save file
            field.data.save(target_filename)

        with zipfile.ZipFile(target_filename, "r") as zip_ref:
            # create a temporary directory in which to unzip
            with tempfile.TemporaryDirectory() as temp_dir_zip:
                try:
                    zip_ref.extractall(temp_dir_zip)
                except zipfile.BadZipFile:
                    raise validators.ValidationError("Unable to read module archive.")
                # if metadata.json file does not exist raise a validation error
                # archive should contain at least one metadata.json file
                metadata_paths = list(find_files("metadata.json", temp_dir_zip))
                #metadata_path = os.path.join(temp_dir_zip, "metadata.json")
                #if not os.path.exists(metadata_path):
                if len(metadata_paths)==0:
                    raise validators.ValidationError("Module archive should contain a 'metadata.json' file.")
                # check names of modules
                for metadata_path in metadata_paths:
                    # read the metadata
                    metadata = json.load(open(metadata_path,"r"))
                    if not "name" in metadata:
                        raise validators.ValidationError("Invalid metadata.json file.")
                    # check that there are no installed modules with the same name
                    module_name = metadata["name"]
                    modules = Module.query.where(Module.name==module_name)
                    if modules.count():
                        raise validators.ValidationError(f"A Module named '{module_name}' already exists.")

class JSONValidator(object):
    def __call__(self, form, field):
        try:
            data = json.loads(field.data)
        except:
            raise validators.ValidationError("Must be valid JSON data.")

class StringListValidator(object):
    def __call__(self, form, field):
        # check that the arguments value can be converted to JSON
        data = None
        try:
            data = json.loads(field.data)
        except:
            raise validators.ValidationError(f"Arguments value must be JSON formatted.")
        # check that it's a list and all items are non-empty strings
        if not isinstance(data, list):
            raise validators.ValidationError("Arguments value must be a list.")
        if len(data):
            are_strings = [isinstance(o,str) and (len(o)>0) for o in data]
            if not all(are_strings):
                raise validators.ValidationError("Arguments value must be a list of non-empty strings.")

class ModuleOutputValidator(object):
    def __call__(self, form, field):
        data = json.loads(field.data)
        # type
        if not "type" in data:
            raise validators.ValidationError("Output field must have a 'type' field.")
        types = ["timeseries", "catalog", "timetable"]
        if not data["type"] in types:
            raise validators.ValidationError(f"Output type must be one of the following : {types}.")
        # filename
        if not "filename" in data:
            raise validators.ValidationError("Output must have a 'filename' field.")
        if not isinstance(data["filename"], str):
            raise validators.ValidationError("Filename must be a string.")


class ModuleArgumentDefaultsValidator(object):
    def __call__(self, form, field):
        # check that the arguments value can be converted to JSON
        data = None
        try:
            data = json.loads(field.data)
        except:
            raise validators.ValidationError(f"Arguments defaults value must be JSON formatted.")
        # check that it's a list and all items are non-empty strings
        if not isinstance(data, dict):
            raise validators.ValidationError("Arguments defaults value must be a dictionary.")
        if len(data):
            # check that each key corresponds to a value in the arguments field
            arguments = json.loads(form["arguments"].data)
            are_args = [k in arguments for k in data.keys()]
            if not all(are_args):
                raise validators.ValidationError("Keys must correspond to arguments.")
            # values can be str, int or float
            are_good_type= [isinstance(o,(str,int,float,)) for o in data.values()]
            if not all(are_good_type):
                raise validators.ValidationError("Arguments defaults must be of type str, int, float.")

class PythonVersionValidator(object):
    def __call__(self, form, field):
        # must contain only numeric values and "."
        s = field.data.split(".")
        try:
            l = [int(w) for w in s]
        except:
            raise validators.ValidationError("Invalid python version.")


