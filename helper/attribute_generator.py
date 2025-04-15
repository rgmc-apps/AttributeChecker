import base64
import csv
import json
import requests
import os
import time
from datetime import datetime
from io import StringIO
from pathlib import Path
from config import WITH_DESCRIPTION, DIRECTORY_PATH, API_KEY, PROMPT_NODESC, PROMPT_WDESC, GPT_LIMIT


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
            with open(image_path + ".txt", "r") as description_file:
                return ''.join(description_file.readlines())
        else:
            self.__logger.warning('{} has no corresponding text file'.format(image_path)) 

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
        "model": "gpt-4.1",

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
        retval = []

        for file in imagelist:
            base64_image = self.__encode_image(file)

            if self.__with_description:
                description = self.__get_product_description(file)  # one long string
                self.__prompt = '{} {}'.format(self.__prompt, description)
                
            if entry_count == GPT_LIMIT:
                self.__logger.info('Rate limit reached for gpt-4.1 on requests per min (RPM): Limit 3, Used 3. Will pause for 20 seconds.')
                time.sleep(21)
                entry_count = 0

            self.__logger.info('Start Prompt for {}'.format(file))
            response = self.__get_gpt_response(base64_image)
            entry_count += 1

            json_dict = response.json()
            choices = json_dict.get('choices', [])

            # print(json_dict)

            if choices:
                message = choices[0].get('message', {})
                csv_str = message.get('content')      
                csv_reader = csv.reader(StringIO(csv_str))
                ignore_line = next(csv_reader)

                if saved_header is None:
                    saved_header = ['filename'] + next(csv_reader)

                if attributes_table:
                   ignore_line = next(csv_reader)

                row = next(csv_reader)
                row = list(map(lambda s: s.strip(), row))
                attributes_table = attributes_table + [[Path(file).name] + row]
            else:
                self.__logger.warning('{} - Not Processed by GPT. Response unexpected: {}'.format(file, response.json()))

        if attributes_table:
            # filename = os.path.join(self.__filepath, 'attributes-{}.csv'.format(datetime.now().strftime('%FT%XZ')))
            filename = 'attributes_{}.csv'.format(datetime.now().strftime("%Y%m%dT%H%M"))
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(saved_header)
                writer.writerows(attributes_table)

        