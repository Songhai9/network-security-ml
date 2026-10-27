import os
import sys

from networksecurity.cloud.s3_syncer import S3Sync
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.app_logging.logger import logger

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer

from networksecurity.entity.config_entity import(
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
)

from networksecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArtifact,
    ModelTrainerArtifact,
)

from networksecurity.constant.training_pipeline import TRAINING_BUCKET_NAME
from networksecurity.constant.training_pipeline import SAVED_MODEL_DIR
import sys


class TrainingPipeline:
    def __init__(self):
        self.training_pipeline_config = TrainingPipelineConfig()
        self.s3_sync = S3Sync()


    def start_data_ingestion(self) -> DataIngestionArtifact:
        try:
            logger.info("Entered the start_data_ingestion method of TrainingPipeline class")
            data_ingestion_config = DataIngestionConfig(self.training_pipeline_config)
            logger.info('Start data ingestion')
            data_ingestion = DataIngestion(data_ingestion_config=data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            logger.info("Data ingestion completed and artifact is created")
            return data_ingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact) -> DataValidationArtifact:
        try:
            logger.info("Entered the start_data_validation method of TrainingPipeline class")
            data_validation_config = DataValidationConfig(self.training_pipeline_config)
            data_validation = DataValidation(
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_config=data_validation_config,
            )
            logger.info("Initiate the data validation")
            data_validation_artifact = data_validation.initiate_data_validation()
            logger.info("Data validation completed and artifact is created")
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def start_data_transformation(self, data_validation_artifact: DataValidationArtifact) -> DataTransformationArtifact:
        try:
            logger.info("Entered the start_data_transformation method of TrainingPipeline class")
            data_transformation_config = DataTransformationConfig(self.training_pipeline_config)
            data_transformation = DataTransformation(
                data_validation_artifact=data_validation_artifact,
                data_transformation_config=data_transformation_config,
            )
            logger.info("Initiate the data transformation")
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            logger.info("Data transformation completed and artifact is created")
            return data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def start_model_trainer(self, data_transformation_artifact: DataTransformationArtifact) -> ModelTrainerArtifact:
        try:
            logger.info("Entered the start_model_trainer method of TrainingPipeline class")
            model_trainer_config = ModelTrainerConfig(self.training_pipeline_config)
            model_trainer = ModelTrainer(
                model_trainer_config=model_trainer_config,
                data_transformation_artifact=data_transformation_artifact,
            )
            logger.info("Initiate the model trainer")
            model_trainer_artifact = model_trainer.initiate_model_trainer()
            logger.info("Model trainer completed and artifact is created")
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    def sync_artifacts_dir_to_s3(self):
        try:
            aws_bucket_url = f's3://{TRAINING_BUCKET_NAME}/artifact/{self.training_pipeline_config.timestamp}'
            self.s3_sync.sync_folder_to_s3(folder=self.training_pipeline_config.artifact_dir, aws_bucket_url=aws_bucket_url)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def sync_saved_model_dir_to_s3(self):
        try:
            aws_bucket_url = f's3://{TRAINING_BUCKET_NAME}/final_models/{self.training_pipeline_config.timestamp}'
            self.s3_sync.sync_folder_to_s3(folder=self.training_pipeline_config.model_dir, aws_bucket_url=aws_bucket_url)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def run_pipeline(self):
        try:
            logger.info("Entered the run_pipeline method of TrainingPipeline class")
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact = self.start_data_transformation(data_validation_artifact=data_validation_artifact)
            model_trainer_artifact = self.start_model_trainer(data_transformation_artifact=data_transformation_artifact)
            logger.info("Training pipeline completed successfully")
            self.sync_artifacts_dir_to_s3()
            self.sync_saved_model_dir_to_s3()
        except Exception as e:
            raise NetworkSecurityException(e, sys)

