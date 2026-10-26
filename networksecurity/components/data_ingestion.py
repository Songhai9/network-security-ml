from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.app_logging.logger import logger

## Configuration of the Data Ingestion Config

from networksecurity.entity.config_entity import DataIngestionConfig   
from networksecurity.entity.artifact_entity import DataIngestionArtifact

import os
import sys
import pandas as pd
import numpy as np
import pymongo
from typing import List
from sklearn.model_selection import train_test_split

from dotenv import load_dotenv
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_collection_as_dataframe(self):
        '''
        Read data from MongoDB
        '''
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            with pymongo.MongoClient(MONGODB_URL) as mongo_client:
                collection = mongo_client[database_name][collection_name]
                df = pd.DataFrame(list(collection.find()))

            if df.empty:
                raise ValueError(
                    f"MongoDB collection '{database_name}.{collection_name}' is empty."
                )

            if "_id" in df.columns.to_list():
                df = df.drop("_id", axis=1)

            df.replace({'na': np.nan}, inplace=True)
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_data_to_feature_store(self, df: pd.DataFrame):
        try:
            feature_store_dir = self.data_ingestion_config.feature_store_dir
            # Create folder
            dir_path = os.path.dirname(feature_store_dir)
            os.makedirs(dir_path, exist_ok=True)
            df.to_csv(feature_store_dir, index=False, header=True)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def split_data_as_train_test(self, df: pd.DataFrame):
        try:
            train_set, test_set = train_test_split(
                df,
                test_size=self.data_ingestion_config.train_test_split_ratio,
                random_state=42,
            )
            logger.info("Performed train test split on the dataset")
            logger.info(
                'Exited split_data_as_train_test method of DataIngestion class'
            )
            # Create folder
            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)

            train_set.to_csv(
                self.data_ingestion_config.training_file_path, index=False, header=True
            )
            test_set.to_csv(
                self.data_ingestion_config.testing_file_path, index=False, header=True
            )
            
            logger.info(
                f"Exported training dataset to file: [{self.data_ingestion_config.training_file_path}] and testing dataset to file: [{self.data_ingestion_config.testing_file_path}]"
            )
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_ingestion(self):
        try:
            df = self.export_collection_as_dataframe()
            self.export_data_to_feature_store(df)
            self.split_data_as_train_test(df)
            dataingestionartifact = DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path,
            )
            return dataingestionartifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
