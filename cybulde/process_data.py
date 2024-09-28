from cybulde.config_schemas.config_schema import Config
from cybulde.utils.config_utils import get_config
from cybulde.utils.aws_utils import get_secret
from cybulde.utils.data_utils import get_raw_data_with_version


@get_config(config_path="../configs", config_name="config")
def process_data(config: Config) -> None:
    print(config)
    version="v8"
    data_local_save_dir= "./data/raw"
    dvc_remote_repo ="https://github.com/longtongster/project_template.git"
    dvc_data_folder= "./data/raw"
    github_user_name= "longtongster"
    github_access_token= get_secret()

    get_raw_data_with_version(
    version=version,
    data_local_save_dir= data_local_save_dir,
    dvc_remote_repo =dvc_remote_repo,
    dvc_data_folder= dvc_data_folder,
    github_user_name= github_user_name,
    github_access_token= github_access_token)




if __name__ == "__main__":
    process_data()  # type: ignore
