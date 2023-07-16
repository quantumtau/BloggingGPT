import os
import sys
import time
import requests
import openai
from serpapi import GoogleSearch
from dotenv import load_dotenv
from termcolor import colored
from tqdm import tqdm
import colorama
colorama.init(autoreset=True)
from config import Config

load_dotenv()

cfg = Config()

# Configure OpenAI API key
try:
    openai.api_key = cfg.openai_api_key
    browserless_api_key = cfg.browserless_api_key
    llm_model = cfg.llm_model
except KeyError:
    sys.stderr.write("OpenAI key configuration failed.")
    exit(1)

def write_skeleton(title):
    prompt = """Propose a structure for an article following """+title+"""". 
    Make sure you include headings - H2, H3, H4.
    Please ensure to include actual names in the structure.
    Include description for each section.
    Add FAQ section if relevant. Strictly follow the example structure of JSON:
    
    {
    "Title": "The Role of Energy Efficiency in Home Design",
    "Description": "This article focuses on the importance and incorporation of energy efficiency in home design and its resulting benefits",
    "Sections": [
        {
            "Heading_H2": "Incorporating Energy Efficiency in Home Design",
            "Description": "A detailed guide on how energy efficiency can be embedded into home design, with sub-sections including",
            "SubSections": [
                {
                "Heading_H3": "Passive Design Strategies",
                "Description": "Explanation of passive design strategies to optimize energy efficiency."
                },
                {
                "Heading_H3": "Selecting Efficient Appliances",
                "Description": "Guide on choosing energy-efficient appliances for the home."
                },
                {
                "Heading_H3": "Material Selection for Energy Efficiency",
                "Description": "Discussion on how material selection impacts energy efficiency and the best materials to choose.",
                  "SubSections": [
                      {
                      "Heading_H4": "Insulation Materials",
                      "Description": "Analysis on the role of insulation materials in enhancing energy efficiency."
                      },
                      {
                      "Heading_H4": "Window Materials",
                      "Description": "Guide to choosing energy-efficient window materials."
                      }
                  ]
                }
            ]
        }
    ]
}"""

    chunked_output = ""
    for chunk in openai.ChatCompletion.create(
            model=llm_model,
            stream=True,
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'system', 'content': "You're an expert in blogging and SEO."},
                {'role': 'system', 'content': 'Your name is BloggingGPT.'},
                {'role': 'system', 'content': 'Return the output as JSON.'},
                {"role": "user", "content": prompt}
            ]
    ):
        content = chunk["choices"][0].get("delta", {}).get("content")
        if content is not None:
            #print(content, end='')
            chunked_output += content

    return chunked_output