import logging
import traceback

logging.basicConfig(level=logging.INFO, filename="runtime.log", filemode="w", format="%(asctime)s - %(levelname)s - %(message)s")

DEBUG = True

def log(message):
    if DEBUG: print(message)
    logging.info(message)

def log_debug(message):
    logging.debug(message)

def log_err(message):
    if DEBUG: print(message)
    # append stack trace to message
    message = traceback.format_exc(chain=False) + message
    logging.error(message)