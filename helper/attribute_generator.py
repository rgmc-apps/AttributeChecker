import base64
import csv
import json
import requests
import os
import time
from datetime import datetime
from io import StringIO
from pathlib import Path
from config import WITH_DESCRIPTION, DIRECTORY_PATH, API_KEY, PROMPT_NODESC, PROMPT_WDESC, GPT_LIMIT, GPT_VERSION


class AttributeGenerator(object):
    """GPT image attribute generator main class. 
       Transferred functions from the script provided.
    """

    def __init__(self, logger):
        self.__with_description = WITH_DESCRIPTION
        self.__filepath = DIRECTORY_PATH
        self.__apikey = API_KEY
        self.__rpm_limit = GPT_LIMIT
        self.__logger = logger
        self.__gpt_version = GPT_VERSION

        # Determine what prompt will be used
        if self.__with_description:
            self.__prompt = PROMPT_WDESC
        else:
            self.__prompt = PROMPT_NODESC

    # Function to encode the image
    def __encode_image(self, image_path):
        if os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        else:
            self.__logger.warning('{} image file does not exists'.format(image_file)) 
        
    
    # Function to add description
    def __get_product_description(self, image_path):
        if os.path.exists(image_path + ".txt"):
            with open(image_path.strip().lower() + ".txt", "r") as description_file:
                return ''.join(description_file.readlines())
        else:
            self.__logger.warning('{}.txt has no corresponding text file'.format(image_path)) 

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
        "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        return response
    
    def main(self):
        """Class Main Function. Also Transferred from the provided script."""
        imagelist = self.__get_image_filepaths()
        attributes_table: list[list[str]] = []
        saved_header: list[str] = None
        entry_count = 0  # this will watch the requests per minute (rpm) of gpt 4.1

        self.__logger.info(imagelist)

        for file in imagelist:
            base64_image = self.__encode_image(file)

            if self.__with_description:
                description = self.__get_product_description(file)  # one long string
                self.__prompt = '{} \n {}'.format(self.__prompt, description)
                
            if entry_count >= GPT_LIMIT:
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
                row = []

                # find csv contents:
                for line in csv_reader:
                    if '```csv' in line:
                        content_headers = next(csv_reader)
                        row = next(csv_reader)
                        break

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
            desc = 'WITHDESC' if self.__with_description else 'NODESC'
            filename = '{}/attributes_{}_{}.csv'.format(DIRECTORY_PATH,desc, datetime.now().strftime("%Y%m%dT%H%M"))
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(saved_header)
                writer.writerows(attributes_table)

        