# import logging
# import os

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
# file_handler = logging.FileHandler(f"{os.path.dirname(__file__)}/error.log", mode="w")
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)

# logger.warning("Hello")

from xmlrpc.client import Unmarshaller


unmatched_names = ""
unmatched_names += "hello"+ " Not Found in Customer Data"

print(unmatched_names)


# input()

# class logger():
#     def __init__(self):
#         logger = logging.getLogger(__name__)
#         logger.setLevel(logging.DEBUG)
#         formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
#         file_handler = logging.FileHandler("error.log", mode="w")
#         file_handler.setFormatter(formatter)
#         logger.addHandler(file_handler)
#         self.logger = logger
#     def get_logger(self):
#         return self.logger

# loggerr = logger()