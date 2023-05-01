from invoke import task

from raya.model_job_submitter import ModelJobSubmitter



@task
def actor_deploy(c,  class_path, name=None, code_folder=None, requirements=None, folder=None, namespace: str=None, ray_url: str=None, copy_env_vars: bool= False):
    ray_url = ray_url or "http://127.0.0.1:8265"
    jobber = ModelJobSubmitter(ray_url=ray_url)
    jobber.submit_job(class_path, name, code_folder, folder, requirements, namespace, copy_env_vars)
