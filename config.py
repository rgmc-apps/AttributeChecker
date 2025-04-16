import os

# OpenAI API Key
# See https://platform.openai.com/docs/quickstart?context=python
# for how to get your API key
# Provided new api key because the existing key has limitations for execution for the latest chatgpt version
API_KEY = ""

# Path to the images
# New Feature: Now able to get all image files (.web3) on a given directory, thus making it able to process per batch   
DIRECTORY_PATH = r""

# Change to consider description text file 
WITH_DESCRIPTION = True 

# Current working Version of chatGPT
GPT_VERSION = 'gpt-4.1'

# Current Versions (gpt-4.1) requests per minute 
GPT_LIMIT = 10

# With product description - this will be used if WITH_DESCRIPTION is set to True:
PROMPT_WDESC = "Tell me attributes of the clothing in the image in CSV format(make sure to enclose with ```csv ```). I would like to know its color, neckline shape, sleeve length, sleeve style, and fit (has to be one of regular or slim). You can also use the product description below to help find the attributes: "

# Without product description - this will be used if WITH_DESCRIPTION is set to False:
PROMPT_NODESC = "Tell me attributes of the clothing in the image in CSV format(make sure to enclose with ```csv ```) with a header line. I would like to know its color, neckline shape, sleeve length, sleeve style, and fit (has to be one of regular or slim)."
