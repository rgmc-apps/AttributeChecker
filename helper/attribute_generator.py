import base64
import csv
import json
import requests
import os
import time
from datetime import datetime
from io import StringIO
from pathlib import Path
from config import API_KEY, GPT_LIMIT, GPT_VERSION, SCRIPT_VERSION, PROMPT_V2
from pprint import pprint


class AttributeGenerator(object):
    """GPT image attribute generator main class. 
       Transferred functions from the script provided.
    """

    def __init__(self, logger, data):
        self.__filepath = data.get('filepath', '')
        self.__apikey = API_KEY
        self.__rpm_limit = GPT_LIMIT
        self.__logger = logger
        self.__gpt_version = GPT_VERSION
        self.__with_description = True
        self.__attributes = data.get('attributes', '')

        # Path to the images
        # New Feature: Now able to get all image files (.web3) on a given directory, thus making it able to process per batch   

        if SCRIPT_VERSION == 1: 
            # With product description - this will be used if WITH_DESCRIPTION is set to True:
            self.__prompt_wdesc = "Tell me attributes of the clothing in the image in CSV format(make sure to enclose with ```csv ```). I would like to know its {}. You can also use the product description below to help find the attributes: ".format(self.__attributes)
            # Without product description - this will be used if WITH_DESCRIPTION is set to False:
            self.__prompt_nodesc = "Tell me attributes of the clothing in the image in CSV format(make sure to enclose with ```csv ```) with a header line. I would like to know its {}. Also give a short product description for the clothing".format(self.__attributes)      
        else:
            # New format for the prompt output
            # self.__prompt = open('myPrompt.txt', encoding='utf-8')
            self.__prompt = PROMPT_V2
            
    # Function to encode the image
    def __encode_image(self, image_path):
        if os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        else:
            self.__logger.warning('{} image file does not exists'.format(image_file)) 
    
    def join_and(items):
        return ', '.join(items[:-1]) + ' and '+items[-1]
          
    # Function to add description
    def __get_product_description(self, image_path):
        retval = ''
        if os.path.exists(image_path + "_description.txt"):
            with open(image_path.strip().lower() + ".txt", "r") as description_file:
                return retval.join(description_file.readlines())
        else:
            self.__logger.warning('{}.txt has no corresponding text file'.format(image_path)) 
        
        return retval

    def __get_image_filepaths(self):
        """
        This function will generate the file names in a directory 
        tree by walking the tree either top-down or bottom-up. For each 
        directory in the tree rooted at directory top (including top itself), 
        it yields a 3-tuple (dirpath, dirnames, filenames).
        """
        retval = []
        directory = self.__filepath

        for root, directory, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                if filename.endswith('.webp'):
                    retval.append(filepath)

        return retval 
    
    def __get_gpt_response(self, image_binary):
        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {self.__apikey}"
        }

        payload = {
        "model": self.__gpt_version,

        "messages": [
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": self.__prompt
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_binary}"
                }
                }
            ]
            }
        ],
        "max_tokens": 400
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        return response
    
    def main(self):
        """Class Main Function. Also Transferred from the provided script."""
        imagelist = self.__get_image_filepaths()
        attributes_table: list[list[str]] = []
        saved_header: list[str] = None
        entry_count = 0  # this will watch the requests per minute (rpm) of gpt 4.1
        retval = {
            'message': '',
            'status': '',
            'directory': ''
        }

        self.__logger.info(imagelist)

        if len(imagelist) == 0:
            self.__logger.warning('No images were present in the given directory - {}'.format(self.__filepath))
            retval['message'] = 'No images were present in the given directory'
            retval['status'] = 'Finished'
            return retval
        
        if SCRIPT_VERSION > 1:
            for file in imagelist:
                base64_image = self.__encode_image(file)

                if entry_count >= self.__rpm_limit:
                    self.__logger.info('Rate limit reached for gpt-4.1 on requests per min (RPM): Limit 3, Used 3. Will pause for 20 seconds.')
                    time.sleep(21)

                if file:
                    self.__logger.info('Start Prompt for {}'.format(file))
                    response = self.__get_gpt_response(base64_image)

                    json_dict = response.json()
                    choices = json_dict.get('choices', [])

                    if choices:
                        message = choices[0].get('message', {})
                        csv_str = message.get('content')
                        csv_str = message.get('content')      
                        csv_reader = csv.reader(StringIO(csv_str))
                        # self.__logger.info('Prompt Finished. Full Response Below: \n {} \n'.format(csv_str))
                        text_filename = '{}/{}-{}-description-v2.txt'.format(self.__filepath, Path(file).parent.name, Path(file).stem)     
                        with open(text_filename, "w", encoding="utf-8", newline='\n') as text_file:
                            for line in csv_reader:
                                for char in line: 
                                    if char:
                                        text_file.write('{}'.format(char))
                                text_file.write('\n')
                        
                        self.__logger.info('File successfully created - {}'.format(text_filename))
                        retval['message'] = 'Program Successfully Finished. CSV file generated: {}'.format(text_filename)
                        retval['status'] = 'Success'
                        retval['filename'] = text_filename
                    else:
                       retval['message'] = 'No results were found in the response'
                       retval['status'] = 'Error'
        else:
            for file in imagelist:
                base64_image = self.__encode_image(file)
                description = self.__get_product_description(file)

                if description:
                    self.__prompt = '{} \n {}'.format(self.__prompt_wdesc, description)
                    self.__with_description = True
                else:
                    self.__prompt = self.__prompt_nodesc
                    self.__with_description = False
                    
                if entry_count >= self.__rpm_limit:
                    self.__logger.info('Rate limit reached for gpt-4.1 on requests per min (RPM): Limit 3, Used 3. Will pause for 20 seconds.')
                    time.sleep(21)

                self.__logger.info('Start Prompt for {}'.format(file))
                response = self.__get_gpt_response(base64_image)
                entry_count += 1

                json_dict = response.json()
                choices = json_dict.get('choices', [])
                
                if choices:
                    message = choices[0].get('message', {})
                    csv_str = message.get('content')      
                    csv_reader = csv.reader(StringIO(csv_str))
                    self.__logger.info('Prompt Finished. Full Response Below: \n {} \n'.format(csv_str))
                    content_headers = []
                    main_description = ''
                    row = []

                    # find csv contents:
                    for line in csv_reader:
                        
                        if '```csv' in line:
                            content_headers = next(csv_reader)
                            row = next(csv_reader)
                            continue
                        for char in line:
                            if 'product description' in char.strip().lower(): 
                                desc = next(csv_reader)
                                main_description = ', '.join(desc)
                                text_filename = '{}/{}-{}-description.txt'.format(self.__filepath, Path(file).parent.name, Path(file).stem)
                                with open(text_filename, 'w') as text_file:
                                    att_count = 0
                                    for attribute in row:
                                        text_file.write('{}: {} \n'.format(content_headers[att_count].capitalize(), attribute))
                                        att_count += 1
                                    text_file.write('{}'.format(main_description))
                                continue
                        
                    if content_headers and row:
                        if saved_header is None:
                            saved_header = ['filename'] + content_headers

                        row = list(map(lambda s: s.strip(), row))
                        attributes_table = attributes_table + [[Path(file).name] + row]
                    else:
                        self.__logger.warning('{} - Not Processed, GPT response returned no CSV format'.format(Path(file).name))
                else:
                    self.__logger.warning('{} - Not Processed. Response unexpected: {}'.format(Path(file).name, response.json()))

            if attributes_table:
                foldername = os.path.basename(self.__filepath)
                filename = '{}/{}_attributes_{}.csv'.format(self.__filepath, foldername, datetime.now().strftime("%Y%m%dT%H%M"))
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(saved_header)
                    writer.writerows(attributes_table)
                
                retval['message'] = 'Program Successfully Finished. CSV file generated: {}'.format(filename)
                retval['status'] = 'Success'
                retval['filename'] = filename

        return retval
