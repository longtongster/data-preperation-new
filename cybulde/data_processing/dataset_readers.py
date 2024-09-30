import os
import pandas as pd

from abc import ABC, abstractmethod
from typing import Optional

import dask.dataframe as dd
from cybulde.utils.utils import get_logger

from dask_ml.model_selection import train_test_split
from dvc.api import get_url


class DatasetReader(ABC):
    required_columns = {"text", "label", "split", "dataset_name"}
    split_names = {"train", "dev", "test"}

    def __init__(self,  dataset_dir: str, dataset_name: str) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.dataset_dir = dataset_dir
        self.dataset_name = dataset_name


    def read_data(self):
        train_df, dev_df, test_df = self._read_data()
        df = self.assign_split_names_to_data_frames_and_merge(train_df, dev_df, test_df)
        df["dataset_name"] = self.dataset_name
        if any(required_column not in df.columns.values for required_column in self.required_columns):
            raise ValueError(f"Dataset must contain all required columns: {self.required_columns}")
        #unique_split_names = set(df["split"].unique().compute().tolist())
        unique_split_names = set(df.compute()['split'].unique().tolist())
        if unique_split_names != self.split_names:
            raise ValueError(f"Dataset must contain all required split names: {self.split_names}")
        final_df: dd.core.DataFrame = df[list(self.required_columns)]
        return final_df


    @abstractmethod
    def _read_data(self) -> tuple[dd.core.DataFrame, dd.core.DataFrame, dd.core.DataFrame]:
        """
        Read and split dataset into 3 splits: train, dev, test.
        The return value must be a dd.core.DataFrame, with required columns: self.required_columns
        """

    def assign_split_names_to_data_frames_and_merge(
            self,  train_df: dd.core.DataFrame,  
            dev_df: dd.core.DataFrame,  
            test_df: dd.core.DataFrame) -> dd.core.DataFrame:
        
        train_df["split"] = "train"
        dev_df["split"] = "dev"
        test_df["split"] = "test"
        final_df: dd.core.DataFrame = dd.concat([train_df, dev_df, test_df])
        return final_df
    
    def split_dataset(
        self, df: dd.core.DataFrame, test_size: float, stratify_column: Optional[str] = None
    ) -> tuple[dd.core.DataFrame, dd.core.DataFrame]:
        if stratify_column is None:
            return train_test_split(df, test_size=test_size, random_state=1234, shuffle=True)  # type: ignore
        unique_column_values = df[stratify_column].unique()
        first_dfs = []
        second_dfs = []
        for unique_set_value in unique_column_values:
            sub_df = df[df[stratify_column] == unique_set_value]
            sub_first_df, sub_second_df = train_test_split(sub_df, test_size=test_size, random_state=1234, shuffle=True)
            first_dfs.append(sub_first_df)
            second_dfs.append(sub_second_df)

        first_df = dd.concat(first_dfs)  # type: ignore
        second_df = dd.concat(second_dfs)  # type: ignore
        return first_df, second_df


class GHCDatasetReader(DatasetReader):
    def __init__(self,dataset_dir: str, dataset_name: str, dev_split_ratio: float) -> None:
        super().__init__(dataset_dir, dataset_name)
        self.dev_split_ratio: float = dev_split_ratio

    def _read_data(self) -> tuple[dd.core.DataFrame, dd.core.DataFrame, dd.core.DataFrame]:
        self.logger.info(f"Reading dataset GHC dataset ...")
        train_tsv_path: str = os.path.join(self.dataset_dir,"ghc_train.tsv")
        train_df = dd.read_csv(train_tsv_path, sep="\t")
        # print(train_df.head())
        # print(train_df.compute().shape)

        test_tsv_path: str = os.path.join(self.dataset_dir,"ghc_test.tsv")
        test_df = dd.read_csv(test_tsv_path, sep="\t")
        # print(test_df.head())
        # print(test_df.compute().shape)

        train_df["label"] = (train_df["hd"] + train_df["cv"] + train_df["vo"] > 0).astype("int")
        test_df["label"] = (test_df["hd"] + test_df["cv"] + test_df["vo"] > 0).astype("int")
        #print(train_df["label"].value_counts(normalize=True).compute())

        train_df, dev_df = self.split_dataset(train_df, self.dev_split_ratio, stratify_column="label")
        # print(train_df.compute().shape)
        # print(dev_df.compute().shape)
        # #print(train_df.head())
        #print(train_df.compute()["label"].value_counts(normalize=True))

        return train_df, dev_df, test_df

class JigsawToxicCommentsDatasetReader(DatasetReader):
    def __init__(self,dataset_dir: str, dataset_name: str, dev_split_ratio: float) -> None:
        super().__init__(dataset_dir, dataset_name)
        self.dev_split_ratio: float = dev_split_ratio
        self.columns_for_labels = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']

    def _read_data(self) -> tuple[dd.core.DataFrame, dd.core.DataFrame, dd.core.DataFrame]:
        self.logger.info(f"Reading {self.__class__.__name__} dataset")
        train_csv_path: str = os.path.join(self.dataset_dir,"train.csv")
        train_df = dd.read_csv(train_csv_path, sep=",")
        train_df = self.get_test_and_label_columns(train_df)
        # print(train_df.head())
        # print(train_df.compute().shape)
        
        train_df, dev_df = self.split_dataset(train_df, self.dev_split_ratio, stratify_column="label")
        # print(train_df.compute().shape)
        # print(dev_df.compute().shape)

        test_labels_csv_path = os.path.join(self.dataset_dir,"test_labels.csv")
        test_labels_df = dd.read_csv(test_labels_csv_path)
        # print(test_labels_df.head())

        test_csv_path: str = os.path.join(self.dataset_dir,"test.csv")
        test_df = dd.read_csv(test_csv_path, sep=",")
        # print(test_df.head())
        # print(test_df.compute().shape)

        test_df = test_df.merge(test_labels_df, on="id")
        test_df = test_df[test_df.toxic!=-1]
        # test_df["label"] = (test_df[self.columns_for_labels].sum(axis=1) > 0).astype("int")
        # test_df = test_df.rename(columns={"comment_text":"text"})
        test_df = self.get_test_and_label_columns(test_df)
        # print(test_df.compute().shape)
        # print(test_df["label"].sum().compute())
        #print(test_df.head())

        return train_df, dev_df, test_df
    
    def get_test_and_label_columns(self, df: dd.core.DataFrame) -> dd.core.DataFrame:
        df["label"] = (df[self.columns_for_labels].sum(axis=1) > 0).astype("int")
        df = df.rename(columns={"comment_text":"text"})
        return df



class DatasetReaderManager:
    def __init__(self, dataset_readers: dict[str, DatasetReader]) -> None:
        self.dataset_readers = dataset_readers

    def read_data(self) -> dd.core.DataFrame:
        dfs = [dataset_reader.read_data() for dataset_reader in self.dataset_readers.values()]
        df: dd.core.DataFrame = dd.concat(dfs)  # type: ignore
        return df

# object = GHCDatasetReader('data/raw/ghc','ghc', 0.5)
# print(object.required_columns)
# df1, df2, df3 = object._read_data()
# print(df1.compute().shape, df2.compute().shape, df3.compute().shape)
# print(df3.head())
# df = object.read_data()
# print(df.compute().shape)
# # rm = DatasetReaderManager()

# object = JigsawToxicCommentsDatasetReader("./data/raw/jigsaw-toxix-comments", "jigsaw", 0.3)
#print(object._read_data())
