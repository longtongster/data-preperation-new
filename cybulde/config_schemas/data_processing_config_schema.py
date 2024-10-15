from hydra.core.config_store import ConfigStore
from omegaconf import MISSING
from pydantic.dataclasses import dataclass

from cybulde.config_schemas.data_processing import dataset_cleaners_schema, dataset_readers_schema
from cybulde.config_schemas.dask_cluster import dask_cluster_schema


@dataclass
class DataProcessingConfig:
    # The main config yaml file is `data_procssing_config.yaml`. This file refers under
    # defaults to `data_processing_config_schema`. This is created in the config below and has
    # as node this class. The values that are MISSING below are set in that yaml file:
    #   - under defaults in the yaml file the reference is set to `dataset_reader_manager`. The
    #     config for this schema is in the `setup_config` below. This is the most complex part
    #     of video 176. The
    #   - the `version` is set at the bottom of the yaml file.
    version: str = MISSING
    data_local_save_dir: str = "./data/raw"
    dvc_remote_repo: str = "https://github.com/longtongster/project_template.git"
    dvc_data_folder: str = "./data/raw"
    github_user_name: str = "longtongster"
    github_access_token: str = "my_secret"

    # This refers to the DatasetReaderManagerConfig in dataset_readers_schema
    dataset_reader_manager: dataset_readers_schema.DatasetReaderManagerConfig = MISSING

    dataset_cleaner_manager: dataset_cleaners_schema.DatasetCleanerManagerConfig = MISSING

    dask_cluster: dask_cluster_schema.LocalDaskClusterConfig = MISSING

# This is the central place to call all schemas created in the `config_schema` directory
# this setup_config is called in the `utils.config_utils.get_config` function that is used
# in process_data.py
def setup_config() -> None:
    dataset_readers_schema.setup_config()
    dataset_cleaners_schema.setup_config()
    dask_cluster_schema.setup_config()

    cs = ConfigStore.instance()
    cs.store(name="data_processing_config_schema", node=DataProcessingConfig)
