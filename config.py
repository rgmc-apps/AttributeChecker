import os

# OpenAI API Key
# See https://platform.openai.com/docs/quickstart?context=python
# for how to get your API key
# Provided new api key because the existing key has limitations for execution for the latest chatgpt version
API_KEY = ""

# Current working Version of chatGPT
GPT_VERSION = 'gpt-4.1'

# Current Versions (gpt-4.1) requests per minute 
GPT_LIMIT = 10

SCRIPT_VERSION = 2

GENERATE_TEXT = True

PROMPT_V2 = """
Make me a product description of the attached photo. follow the format below for the result \n
“[Product Title in all caps] \n
[One-liner Hook/Tagline in All Caps, optional but encouraged] \n
[Descriptive Paragraph] \n
A 2-3 sentence paragraph describing the item with key benefits woven in naturally. Talk about versatility, fit, material, and suggested use. \n
✅ Why You'll Love It [Items should be one short sentence only] \n
Material - [Actual material made, Feel, weight, breathability, structure] \n
Style - [Occasion-fit or lifestyle relevance] \n
Fit -[Body feel, cinch, looseness] \n
Details - [Standout design features] \n
Sleeves - [Length and weather-appropriateness] \n
Sizing - [Fit info and reference to size chart] \n
Design - [Observable colors and Print if visible]
💬 FAQs \n
Add FAQ - [Yes/No, with added explanation] \n
📦 Shopping Info \n
Fast Shipping Nationwide \n
📌 Sizing & Color Notice \n
Color may appear slightly different due to lighting or screen settings. For best fit, please refer to our size chart in the product photos. \n
Need help? Message us about size help, returns, or product info.” \n

Tags: [Possible tags that can be used in the product in list form]
"""