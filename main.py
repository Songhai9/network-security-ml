from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.entity.config_entity import DataValidationConfig, DataTransformationConfig, DataIngestionConfig, ModelTrainerConfig
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer
from networksecurity.app_logging.logger import logger
from networksecurity.entity.config_entity import TrainingPipelineConfig
import sys

if __name__ == "__main__":
    try:
        trainingpipelineconfig = TrainingPipelineConfig()
        dataingestionconfig = DataIngestionConfig(trainingpipelineconfig)
        dataingestion = DataIngestion(dataingestionconfig)
        logger.info("Enter the try block")
        logger.info("Starting data ingestion")
        dataingestionartifact = dataingestion.initiate_data_ingestion()
        logger.info('Data Ingestion completed')
        print(f'Data ingestion artifact: {dataingestionartifact}\n')
        data_validation_config = DataValidationConfig(trainingpipelineconfig)
        data_validation = DataValidation(
            data_ingestion_artifact=dataingestionartifact,
            data_validation_config=data_validation_config,
        )
        logger.info("Starting data validation")
        data_validation_artifact = data_validation.initiate_data_validation()
        logger.info("Data validation completed")
        print(f'Data validation artifact: {data_validation_artifact}\n')
        data_transformation_config = DataTransformationConfig(trainingpipelineconfig)
        data_transformation = DataTransformation(
            data_validation_artifact=data_validation_artifact,
            data_transformation_config=data_transformation_config,
        )
        logger.info("Starting data transformation")
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        logger.info("Data transformation completed")
        print(f'Data transformation artifact: {data_transformation_artifact}\n')

        logger.info('Model training started')
        
        model_trainer_config = ModelTrainerConfig(trainingpipelineconfig)
        model_trainer = ModelTrainer(
            model_trainer_config=model_trainer_config,
            data_transformation_artifact=data_transformation_artifact,
        )
        model_trainer_artifact = model_trainer.initiate_model_trainer()
        logger.info('Model training completed')
        print(f'Model trainer artifact: {model_trainer_artifact}\n')


    except Exception as e:
        raise NetworkSecurityException(e, sys)