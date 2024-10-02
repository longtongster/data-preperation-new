from cybulde.config_schemas.data_processing_config_schema import DataProcessingConfig
from cybulde.utils.config_utils import get_config
from cybulde.utils.aws_utils import get_secret
from cybulde.utils.data_utils import get_raw_data_with_version
from omegaconf import OmegaConf
from hydra.utils import instantiate


# the directory `configs` contains the `data_processing_config.yaml`
@get_config(config_path="../configs", config_name="data_processing_config")
def process_data(config: DataProcessingConfig) -> None:
    #print(config)
    print(60 * "*")
    print(OmegaConf.to_yaml(config))
    print(60 * "*")
    #print(get_secret())

    # get_raw_data_with_version(
    #     version=config.version,
    #     data_local_save_dir= config.data_local_save_dir,
    #     dvc_remote_repo =config.dvc_remote_repo,
    #     dvc_data_folder= config.dvc_data_folder,
    #     github_user_name= config.github_user_name,
    #     github_access_token= get_secret())

    # print(config.dataset_reader_manager)
    dataset_reader_manager = instantiate(config.dataset_reader_manager)
    dataset_cleaner_manager = instantiate(config.dataset_cleaner_manager)
    # print(dataset_reader_manager)
    # # print(dataset_reader_manager)
    df = dataset_reader_manager.read_data().compute()
    sample_df = df.sample(n=5)
    for idx, row in sample_df.iterrows():
        print(60 * "*")
        print(idx)
        text =row['text']
        print(text)
        cleaned_text = dataset_cleaner_manager(text) 
        print(cleaned_text)       
    # print(df.head())
    # print(df.compute().shape)
    # # print(df["dataset_name"].unique().compute())
    # print(df.compute()['dataset_name'].unique())

    #dataset_cleaner_manager = instantiate(config.dataset_cleaner_manager)
    
 

if __name__ == "__main__":
    process_data()  # type: ignore
