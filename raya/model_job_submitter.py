import os
from pathlib import Path
from pprint import pprint
import time
from typing import *

from ray.job_submission import JobStatus, JobSubmissionClient

import raya
# from raya.component_loader import get_requirements, get_requirements_path

from raya import deploy_model
from raya.component_loader import get_requirements_new, get_requirements
from raya.deploy_model import load_subclasses

DEFAULT_EXCLUDES = [".git", "env", "venv", ".env", ".venv", "model_data", "tmp_env", "tmp", "locust", "data",
                    "data_updated", "upload", "logs", "logs_updated"]

# def get_requirements_new(model_config):
#     pass
"""
The key concept to know here is that when we call `ray job submit` with the python api
job_id = self.client.submit_job(
    # Entrypoint shell command to execute
    entrypoint=entrypoint_cmd,
    runtime_env=runtime_env,

    the entrypoint command is run on an isolated environment on the cluster.

Ray will copy the `working_dir` to some isolated environnment, install the `pip` libraries in the environment
AND then run the command specified in `entrypoint` in that environment(not in the environment the job is submitted).

What this means is even if the environment where the job submitter is run from does not have a library A but we specify
library in `pip` of `runtime_env`, the script mentioned in `entrypoint` will work even if it depends on library A(as it
runs in an isolated environment)
"""


def derive_class_name(class_path: str, module):
    # python introspection. get classes in a file
    # https://stackoverflow.com/questions/8809472/how-do-i-get-classes-in-a-file-in-python
    a_classes = load_subclasses(module, class_path, raya.Actor)
    if a_classes:
        return a_classes[0].__name__
    else:
        return None


# def derive_class_path(code_folder: str, exclude_folders: List[str] = None):
#     # walk recursively through code_folder, filtering out exclude_folders
#     exclude_folders = exclude_folders or DEFAULT_EXCLUDES
#     files = []
#     for root, dirs, files in os.walk(code_folder, topdown=True):
#         dirs[:] = [d for d in dirs if d not in exclude_folders]
#         for name in files:
#             if name.endswith(".py"):
#                 files.append(os.path.join(root, name))
#     for f in files:
#         if derive_class_name(f)
class ModelJobSubmitter:
    def __init__(self, ray_url: str = None):
        ray_url = ray_url if ray_url else os.environ["RAY_ADDRESS"]
        self.client = JobSubmissionClient(ray_url)
        self.ray_url = ray_url

    def submit_job(self, class_path, name: str = None,
                   code_folder: str = None,
                   folder: str = None,
                   requirements: str = None,
                   namespace: str = None,
                   copy_env_vars: bool = False,
                   exclude_folders: List[Path] = None):
        namespace = namespace or ""
        folder = folder or ""
        code_folder = code_folder or os.getcwd()
        exclude_folders = exclude_folders or DEFAULT_EXCLUDES
        working_dir = code_folder
        deploy_model_file = deploy_model.__file__
        class_file_path, class_name = class_path.split(":")

        # class_file_path = class_file_path or  derive_class_path(code_folder)
        _file = class_file_path
        # TODO: if you move to auto discovery of requirements file, then check out `get_requirements`
        requirements = get_requirements(requirements)

        file_path = str(_file)
        # module_name = os.path.splitext(file_path)[0].replace("/", ".")
        # module_name = module
        module_name = get_module(code_folder, class_file_path)

        class_name = class_name or derive_class_name(class_file_path, module_name)
        name = name or class_name
        # if not artifact_folder:
        #     entrypoint_cmd = (
        #         f"python {deploy_model_file}  --name={model_config.name} --working_dir={working_dir} --model_registry="
        #         f"{model_registry_path} --module={module_name}"
        #     )
        # else:
        #     entrypoint_cmd = (
        #         f"python {deploy_model_file}  --name={model_config.name} --working_dir={working_dir} --model_registry="
        #         f"{model_registry_path} --module={module_name} --artifact_folder={artifact_folder}"
        #     )

        entrypoint_cmd = (
            f"python {deploy_model_file}  --name={name} --class_name={class_name} --class_path={class_file_path} --module"
            f"={module_name} --folder={folder} --namespace={namespace}"
        )

        runtime_env = {
            "working_dir": working_dir,
            "pip": {"packages": requirements},
            "env_vars": get_env_vars(copy_env_vars),
            "excludes": exclude_folders,
            "config": {"setup_timeout_seconds": 1800},
        }

        print("Job Submitter: Deploying Runtime Env")
        pprint(runtime_env)
        print("Job Submitter: Entrypoint Cmd")
        pprint(entrypoint_cmd)

        job_id = self.client.submit_job(
            # Entrypoint shell command to execute
            entrypoint=entrypoint_cmd,
            runtime_env=runtime_env,
        )

        print(f"Deploying Job:{job_id} for instance_name:{name}")
        self.wait_until_status(job_id=job_id)
        return job_id

    def wait_until_status(
            self,
            job_id: str,
            status_to_stop_waiting: Set[JobStatus] = None,
            timeout_seconds: int = 30 * 60,
            sleep_seconds=10,
    ):
        status_to_stop_waiting = status_to_stop_waiting or {JobStatus.SUCCEEDED, JobStatus.STOPPED, JobStatus.FAILED}
        start = time.time()
        while time.time() - start <= timeout_seconds:
            status = self.client.get_job_status(job_id)
            print(f"status: {status}")
            logs = self.logs(job_id)
            print(logs)
            if status in status_to_stop_waiting:
                if not logs:
                    print("*********************************************")
                    print("No Job Logs. To troubleshoot:")
                    print(" - check for comments in requirements file")
                    print(
                        " - Go to http://localhost:8265. Click on Logs and the url and check "
                        "runtime_env_setup-<some_number>"
                    )
                    print("*********************************************")
                break
            time.sleep(sleep_seconds)

    def logs(self, job_id: str):
        return self.client.get_job_logs(job_id)



def get_env_vars(copy_env_vars: bool) -> Dict:
    if copy_env_vars:
        return {k: v for k, v in os.environ.items()}
    else:
        return {}

def get_module(code_folder, class_path):
    relative_path = Path(class_path).relative_to(code_folder)  # tf1/actor.py

    relative_path = relative_path.with_suffix("")  # tf1/actor

    relative_path = relative_path.as_posix().replace("/", ".")

    return relative_path
