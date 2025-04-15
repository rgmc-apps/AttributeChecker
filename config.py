import os

# OpenAI API Key
# See https://platform.openai.com/docs/quickstart?context=python
# for how to get your API key
API_KEY = ""

# Path to the images
# New Feature: Now able to get all image files (.web3) on a given directory, thus making it able to process per batch   
DIRECTORY_PATH = os.getcwd()
# DIRECTORY_PATH = os.path.join(folder_dir, '1st batch')

# Change to consider description text file 
WITH_DESCRIPTION = False 

# Current Versions (gpt-4.1) requests per minute 
GPT_LIMIT = 3

# With product description:
PROMPT_WDESC = "Tell me attributes of the clothing in the image in CSV format. I would like to know its color, neckline shape, sleeve length, sleeve style, and fit (has to be one of regular or slim). You can also use the product description below to help find the attributes: "
# Without product description:
PROMPT_NODESC = "Tell me attributes of the clothing in the image in CSV format with a header line. I would like to know its color, neckline shape, sleeve length, sleeve style, and fit (has to be one of regular or slim)."
