"""
The key concept here is that once we create a long lived ray cluster, we can then deploy named actors to that cluster.

Then we can independently deploy Ray Serve Deployments to the same ray cluster and access these long lived actors
by their name.
"""

import importlib
import importlib.util
import inspect
import os
from os.path import relpath
import sys
from typing import *

import ray


import argparse
def get_module_name(file_path: str, working_dir: str):
    return relpath(os.path.splitext(file_path)[0], working_dir).replace("/", ".")


def relative_path(file_path: str, working_dir: str):
    relative_file_path = relpath(file_path, working_dir)
    return relative_file_path


def get_class(class_name: str, file_path: str, module: str):
    print(f"class_name:{class_name}")
    print(f"file_path:{file_path}")
    print(f"module:{module}")
    print('================================')

    foo = load_module(file_path, module)
    my_class = getattr(foo, class_name)
    return my_class


def load_module(file_path, module):
    spec = importlib.util.spec_from_file_location(module, file_path)
    foo = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = foo
    spec.loader.exec_module(foo)
    return foo

def load_subclasses(module, file_path, actor_class):
    all_subclasses = []
    foo = load_module(file_path, module)
    for name, obj in inspect.getmembers(foo):
        if inspect.isclass(obj):
            if issubclass(obj, actor_class) and (obj is not actor_class):
                all_subclasses.append(obj)

    return all_subclasses

# def create_named_actor(a_cls, a_name: str, an_args: Tuple, a_kwargs: Dict):
#     namespace = "serve"
#     print(f"Namespace: {namespace}. Creating Named Actor:{a_name} with args:{an_args}, kwargs: {a_kwargs}")
#     try:
#         actor_handle = ray.get_actor(a_name, namespace=namespace)
#         ray.kill(actor_handle)
#         print(f"Killing Previous Named Actor:{a_name}")
#     except:
#         print(f"No Previous Named Actor:{a_name}")
#         pass
#
#     named_actor = (
#         ray.remote(a_cls)
#         .options(namespace=namespace, name=a_name, get_if_exists=True, lifetime="detached")
#         .remote(*an_args, **a_kwargs)
#     )
#
#     print(f"Created Named Actor:{a_name}")
#     a = ray.get_actor(a_name, namespace=namespace)
#     print(f"Getting Actor:{a}")
#     return a

def create_named_actor(a_cls, a_name: str, an_args: Tuple, a_kwargs: Dict, namespace:str=None):
    namespace = namespace or "serve"

    print(f"Namespace: {namespace}. Creating Named Actor:{a_name} with args:{an_args}, kwargs: {a_kwargs}")
    try:
        actor_handle = ray.get_actor(a_name, namespace=namespace)
        ray.kill(actor_handle)
        print(f"Killing Previous Named Actor:{a_name}")
    except:
        print(f"No Previous Named Actor:{a_name}")
        pass

    named_actor = (
        ray.remote(a_cls)
        .options(namespace=namespace, name=a_name, get_if_exists=True, lifetime="detached")
        .remote(*an_args, **a_kwargs)
    )

    print(f"Created Named Actor:{a_name}")
    a = ray.get_actor(a_name, namespace=namespace)
    print(f"Getting Actor:{a}")
    return a

def check_init_args(cls, init_kwargs):
    spec = inspect.getfullargspec(cls.__init__)
    args = init_kwargs.keys()
    spec_args = spec.args[1:]

    for arg in args:
        if arg not in spec_args:
            raise ValueError(f"Argument {arg} not in args of {cls}:  {spec_args}")


if __name__ == "__main__":

    ray.init(namespace="serve")

    my_parser = argparse.ArgumentParser()
    my_parser.add_argument("--name", help="name of model instance", required=True)
    my_parser.add_argument("--class_name", help="name of actor", required=True)
    my_parser.add_argument("--class_path", help="path to actor", required=True)
    my_parser.add_argument("--module", help="module name", required=True)
    my_parser.add_argument("--folder", help="artifacts folder")
    my_parser.add_argument("--namespace", help="namespace")
    args = my_parser.parse_args()

    if args.folder:
        init_kwargs = dict(folder=args.folder)
    else:
        init_kwargs = dict()


    # TODO: remove the need to pass module? figure out module from class_path?
    # my_class = get_class(args.class_name, args.class_path, args.module)
    my_class = get_class(args.class_name, args.class_path, args.module)
    check_init_args(my_class, init_kwargs)
    actor = create_named_actor(my_class, args.name, tuple(), init_kwargs, args.namespace)
    print("Actor Model Folder")
    # TODO: If we don't subclass any raya component in the actor, how will we check for the actor being deployed?
    print(ray.get(actor.no_op.remote()))
