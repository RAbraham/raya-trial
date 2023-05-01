from pathlib import Path
from typing import *

# from attribute_prediction_api.components_lib.component_config import ComponentConfig
# from attribute_prediction_api.components_lib.constants import REQUIREMENTS_TXT


# def get_requirements(working_dir: Path, component_config: ComponentConfig) -> List[str]:
#     requirements_file = get_requirements_path(working_dir, component_config)
#     if requirements_file.exists():
#         requirements = requirements_file.read_text().split()
#     else:
#         requirements = []
#
#     return requirements
def get_requirements_new(requirements_file: str, class_file_path: str) -> List[str]:
    if requirements_file:
        requirements = load_requirements(requirements_file)
    else:
        req_path = get_requirements_path(class_file_path)
        if req_path.exists():
            requirements = req_path.read_text().split()
        else:
            requirements = []

    return requirements

def get_requirements(requirements_file: str) -> List[str]:
    if requirements_file:
        requirements = load_requirements(requirements_file)
    else:
        requirements = []
    return requirements

def load_requirements(requirements_file):
    return Path(requirements_file).read_text().split()


def get_requirements_path(class_file_path: str) -> Path:
    class_path = Path(class_file_path)
    code_folder = class_path.parent
    full_path = code_folder / "requirements.txt"
    return full_path

# def get_requirements_path(working_dir, component_config):
#     component_path = component_config.class_path
#     code_folder = component_path.parent
#     full_path = working_dir / code_folder
#     requirements_file = full_path / REQUIREMENTS_TXT
#     return requirements_file
