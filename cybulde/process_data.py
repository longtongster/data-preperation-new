from hydra.utils import instantiate
from omegaconf import OmegaConf

from cybulde.config_schemas.data_processing_config_schema import DataProcessingConfig
from cybulde.utils.aws_utils import get_secret
from cybulde.utils.config_utils import get_config
from cybulde.utils.data_utils import get_raw_data_with_version
from cybulde.utils.utils import get_logger

from dask.distributed import Client
import dask.dataframe as dd
from pathlib import Path

def process_raw_data(df_partition, dataset_cleaner_manager) -> dd.core.Series:
    return df_partition["text"].apply(dataset_cleaner_manager)



# the directory `configs` contains the `data_processing_config.yaml`
@get_config(config_path="../configs", config_name="data_processing_config")
def process_data(config: DataProcessingConfig) -> None:
    logger = get_logger(Path(__file__).name)
    logger.info("Processing raw data ...")

    cluster = instantiate(config.dask_cluster)
    client = Client(cluster)

    try:
        # print(get_secret())

        # get_raw_data_with_version(
        #     version=config.version,
        #     data_local_save_dir=config.data_local_save_dir,
        #     dvc_remote_repo=config.dvc_remote_repo,
        #     dvc_data_folder=config.dvc_data_folder,
        #     github_user_name=config.github_user_name,
        #     github_access_token=get_secret(),
        # )

        # # print(config.dataset_reader_manager)
        dataset_reader_manager = instantiate(config.dataset_reader_manager)
        dataset_cleaner_manager = instantiate(config.dataset_cleaner_manager)
        
        logger.info("Reading raw data ...")
        df = dataset_reader_manager.read_data()
        print(df.head())
        
        logger.info("Cleaning data ...")
        # print(df)
        df = df.assign(cleaned_text=df.map_partitions(process_raw_data, dataset_cleaner_manager=dataset_cleaner_manager, meta=("text","object")))
        # clear
        # df = df.compute()
        print(df.head())
        #print(df.head())
        
        # print(dataset_reader_manager)
        # print(dataset_reader_manager)clear

        # Read the data from ghc twitter, jtd
        # df = dataset_reader_manager.read_data().compute()
        # sample_df = df.sample(n=5)
        # for idx, row in sample_df.iterrows():
        #     print(60 * "*")
        #     print(idx)
        #     text = row["text"]
        #     print(len(text))
        #     print(text)
        #     cleaned_text = dataset_cleaner_manager(text)
        #     print(cleaned_text)
        # # print(df.head())
        # print(df.compute().shape)
        # # print(df["dataset_name"].unique().compute())
        # print(df.compute()['dataset_name'].unique())

        # # dataset_cleaner_manager = instantiate(config.dataset_cleaner_manager)
    finally:
        logger.info("Closing dask client and cluster ...")
        client.close()
        cluster.close()

if __name__ == "__main__":
    process_data()
