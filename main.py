from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.components.data_validation import DataValidation
from networksecurity.app_logging.logger import logger
from networksecurity.entity.config_entity import DataIngestionConfig
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
        print(dataingestionartifact)
        data_validation_config = DataValidation(trainingpipelineconfig)
        data_validation = DataValidation(dataingestionconfig, data_validation_config)
        logger.info("Starting data validation")
        data_validation_artifact = data_validation.initiate_data_validation()
        logger.info("Data validation completed")
        print(data_validation_artifact)
        
    except Exception as e:
        raise NetworkSecurityException(e, sys)