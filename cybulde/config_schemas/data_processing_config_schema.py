from hydra.core.config_store import ConfigStore
from pydantic.dataclasses import dataclass
from omegaconf import MISSING

from cybulde.config_schemas.data_processing import dataset_readers_schema
from cybulde.config_schemas.data_processing import dataset_readers_schema

@dataclass
class DataProcessingConfig:
    version: str = MISSING
    data_local_save_dir: str = "./data/raw"
    dvc_remote_repo: str ="https://github.com/longtongster/project_template.git"
    dvc_data_folder: str = "./data/raw"
    github_user_name:str = "longtongster"
    github_access_token: str = "my_secret"

    dataset_reader_manager: dataset_readers_schema.DatasetReaderManagerConfig = MISSING



# This is the central place to call all schemas created in the `config_schema` directory
# this setup_config is called in the `utils.config_utils.get_config` function that is used
# in process_data.py
def setup_config() -> None:
    dataset_readers_schema.setup_config()

    cs = ConfigStore.instance()
    cs.store(name="data_processing_config_schema", node=DataProcessingConfig)
