from hydra.core.config_store import ConfigStore
from omegaconf import MISSING
from pydantic.dataclasses import dataclass


@dataclass
class DatasetReaderConfig:
    _target_: str = MISSING
    dataset_dir: str = MISSING
    dataset_name: str = MISSING


@dataclass
class GHCDatasetReaderConfig(DatasetReaderConfig):
    _target_: str = "cybulde.data_processing.dataset_readers.GHCDatasetReader"
    dev_split_ratio: float = MISSING


@dataclass
class JigsawToxicCommentsDatasetReaderConfig(DatasetReaderConfig):
    _target_: str = "cybulde.data_processing.dataset_readers.JigsawToxicCommentsDatasetReader"
    dev_split_ratio: float = MISSING


@dataclass
class TwitterDatasetReaderConfig(DatasetReaderConfig):
    _target_: str = "cybulde.data_processing.dataset_readers.TwitterDatasetReader"
    dev_split_ratio: float = MISSING
    test_split_ratio: float = MISSING


@dataclass
class DatasetReaderManagerConfig:
    _target_: str = "cybulde.data_processing.dataset_readers.DatasetReaderManager"
    dataset_readers: dict[str, DatasetReaderConfig] = MISSING
    repartition: bool = True

def setup_config() -> None:
    cs = ConfigStore.instance()
    cs.store(
        name="ghc_dataset_reader_schema", group="dataset_reader_manager/dataset_readers", node=GHCDatasetReaderConfig
    )
    cs.store(
        name="jtc_dataset_reader_schema",
        group="dataset_reader_manager/dataset_readers",
        node=JigsawToxicCommentsDatasetReaderConfig,
    )
    cs.store(
        name="twitter_dataset_reader_schema",
        group="dataset_reader_manager/dataset_readers",
        node=TwitterDatasetReaderConfig,
    )
    cs.store(name="dataset_reader_manager_schema", group="dataset_reader_manager", node=DatasetReaderManagerConfig)
