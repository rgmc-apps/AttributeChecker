import base64
import csv
from io import StringIO
import requests
import os
import logging
from pathlib import Path
from helper.attribute_generator import AttributeGenerator
from logger import LogHandler
from config import *
import traceback

LogHandler('upload-logs')
logger = logging.getLogger('upload-logs')

if __name__ == '__main__':
    try:
        logger.info('Start GPT Image attribute generator')
        logger.info('File Path: {}'.format(DIRECTORY_PATH))
        logger.info('With Lookup Description: {}'.format(WITH_DESCRIPTION))
        AttributeGenerator(logger).main()
    except Exception as e:
        logger.error('Error while running: {} \n {}'.format(e, traceback.format_exc()))