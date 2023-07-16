import os
import sys
import time
from dotenv import load_dotenv
import requests
import openai
from serpapi import GoogleSearch
from termcolor import colored
from tqdm import tqdm
import colorama
import json
from halo import Halo

import articles.writing
from researcher import search
from articles import skeleton
from articles import writing
from articles import seo
from researcher import search
from enhancer import linker
from enhancer import translate
from initiation import kickoff

from config import Config

# Initialize colorama
colorama.init(autoreset=True)

# Load the .env file
load_dotenv()

# Configure OpenAI API key
cfg = Config()
try:
    openai.api_key = cfg.openai_api_key
except KeyError:
    sys.stderr.write("OpenAI key configuration failed.")
    exit(1)


#################################### ARTICLE FUNCTIONS ####################################

article_content = ""
article_title = ""
article_description = ""

def process_section(section, level=2):
    # Call another function here
    section_type = 'section' if level == 2 else 'subsection'
    section_content = ""
    spinner = Halo(text=f'Processing {section_type}: {section[f"Heading_H{level}"]}', spinner='dots')
    spinner.start()
    if section_type == 'section':
        section_content = articles.writing.write_section(article_title,
                                       article_description,
                                       section[f'Heading_H{level}'],
                                       section['Description'])
    if section_type == 'subsection':
        section_content = articles.writing.write_section(article_title,
                                       article_description,
                                       section[f'Heading_H{level}'],
                                       section['Description'])
    spinner.succeed(f"Finished processing {section_type}: {section[f'Heading_H{level}']}")
    if 'SubSections' in section:
        for sub_section in section['SubSections']:
            section_content += process_section(sub_section, level + 1)
    return "\n\n" + f"<h{level}>" + section[f'Heading_H{level}'] + f"</h{level}>" + "\n\n" + section_content

def process_json(json_string):
    global article_content
    spinner = Halo(text='Parsing JSON', spinner='dots')
    spinner.start()
    data = json.loads(json_string)
    article_title = data['Title']
    article_description = data['Description']
    spinner.succeed('Finished parsing JSON')
    #print(f"Article Title: {article_title}")
    #print(f"Article Description: {article_description}")
    for section in data['Sections']:
        article_content += process_section(section)
    return article_content

def article():
    title = ""

    # Check if title is blank
    if not title:
        title = input("Please enter the article title: ")

    #additional_relevant_info = search.go(title)

    spinner = Halo(text='Preparing Structure of Article', spinner='dots')
    spinner.start()
    try:
        article_skeleton = skeleton.write_skeleton(title)
        # print(article_skeleton)
    except Exception as e:
        spinner.fail(str(e))
    else:
        spinner.succeed("Finished writing the article skeleton")

    article_content = title + "\n\n"
    article_content += writing.write_intro(title) + "\n\n"

    # PROCESS SECTIONS
    try:
        article_content += process_json(article_skeleton)
    except Exception as e:
        spinner.fail(str(e))
    else:
        spinner.succeed("Finished processing JSON")

    print(colored("\n\n\n" + "################### FIRST VERSION OF FULL ARTICLE ###################", "green",
                  attrs=["bold"]))
    print(article_content)


#################################### NICHE FUNCTIONS ####################################

def niche_selector():
    kickoff.propose_niche()
    print("Niche")

if __name__ == "__main__":
    article()