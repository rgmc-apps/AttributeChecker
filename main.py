import base64
import csv
from io import StringIO
import requests
import os
import logging
from pathlib import Path, PureWindowsPath
from helper.attribute_generator import AttributeGenerator
from logger import LogHandler
from config import *
import traceback
from datetime import datetime

LogHandler('upload-logs')
logger = logging.getLogger('upload-logs')

if __name__ == '__main__':
    try:
        logger.info('Start GPT Image attribute generator')
        data = {}
        filepath = input('Enter Target Folder Path: (Leave it blank to use the folder where this program is placed): \n')
        
        if filepath:
            filepath = PureWindowsPath(r'{}'.format(filepath))
        else:
            filepath = PureWindowsPath(os.getcwd())

        attributes = input('Enter Specific attributes needed. Separate each item by comma (Leave it blank to use the default attributes) \n')

        if attributes:
            data['attributes'] = attributes
        else: 
            data['attributes'] = 'color, neckline shape, sleeve length, sleeve style, fit(has to be one of regular or slim)'

        data['filepath']  = filepath
        print('filepath-name: ---- {}'.format(filepath.name))
        logger.info('---------{}----------'.format(datetime.now().strftime("%Y-%m-%d-%H:%M")))
        logger.info('Start Program. Target folder: {}'.format(filepath))
        logger.info('Attributes to use: {}'.format(data['attributes']))
        res = AttributeGenerator(logger, data).main()
        logger.info(res.get('message', 'Script finished running'))
    except Exception as e:
        logger.error('Error while running: {} \n {}'.format(e, traceback.format_exc()))