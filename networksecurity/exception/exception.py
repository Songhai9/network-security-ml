"""Custom exception with the source file and line number of an error."""

import sys
from app_logging.logger import logger


class NetworkSecurityException(Exception):
    def __init__(self, error_message, error_details):
        super().__init__(error_message)
        self.error_message = error_message
        _, _, exc_tb = error_details.exc_info()

        self.lineno = exc_tb.tb_lineno
        self.file_name = exc_tb.tb_frame.f_code.co_filename

    def __str__(self):
        return (
            "Error occurred in python script name [{0}] "
            "line number [{1}] error message [{2}]"
        ).format(self.file_name, self.lineno, str(self.error_message))

