import os
import sys
import json
from dotenv import load_dotenv
import openai
from halo import Halo
import colorama
from termcolor import colored

from config import Config
import articles.writing
from articles import skeleton
from articles import writing
from articles import seo
from researcher import search
from enhancer import linker
from enhancer import translate
from initiation import kickoff

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

# Global variables for article content
article_content = ""
article_title = ""
article_description = ""
findings = ""
def process_section(section, level=2):
    """
    Process a section or subsection of the article.
    """
    section_type = 'section' if level == 2 else 'subsection'
    section_content = ""
    spinner = Halo(text=f'Processing {section_type}: {section[f"Heading_H{level}"]}', spinner='dots')
    spinner.start()

    # Write section or subsection
    section_content = articles.writing.write_section(article_title,
                                   article_description,
                                   section[f'Heading_H{level}'],
                                   section['Description'])

    spinner.succeed(f"Finished processing {section_type}: {section[f'Heading_H{level}']}")

    # Process subsections if they exist
    if 'SubSections' in section:
        for sub_section in section['SubSections']:
            section_content += process_section(sub_section, level + 1)

    return "\n\n" + f"<h{level}>" + section[f'Heading_H{level}'] + f"</h{level}>" + "\n\n" + section_content

def process_json(json_string):
    """
    Process the JSON string to generate the article content.
    """
    global article_content
    spinner = Halo(text='Parsing JSON', spinner='dots')
    spinner.start()

    data = json.loads(json_string)
    article_title = data['Title']
    if findings.strip():
        article_description = data['Description'] + f"""{findings}"""
    else:
        article_description = data['Description']


    spinner.succeed('Finished parsing JSON')

    for section in data['Sections']:
        article_content += process_section(section)

    return article_content

def is_json(json_string):
    """
    Check if a string is valid JSON.
    """
    try:
        json.loads(json_string)
    except ValueError:
        return False
    return True

def article():
    """
    Main function to generate the article.
    """
    global findings
    title = input("Please enter the article title: ")

    # RESEARCH
    research = input("Do you want me to research the internet? (y/n): ")
    if research == 'y':
        findings = "Incorporate the following info found on Google: " + search.go(title)
        print(colored("\n" + "################### RESEARCH FINDINGS ###################", "green", attrs=["bold"]))
        print(findings)
    elif research == 'n':
        findings = ""
        pass

    # ARTICLE TYPE
    article_type = input("Do you want Article or Product Review? (a/p): ")
    spinner = Halo(text='Preparing Structure of Article', spinner='dots')
    spinner.start()

    article_skeleton = ""
    while not is_json(article_skeleton):
        try:
            if article_type == 'a':
                article_skeleton = skeleton.write_skeleton(title)
            elif article_type == 'p':
                article_skeleton = skeleton.write_skeleton_product_review(title)
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

def niche_selector():
    """
    Function to select the niche for the article.
    """
    kickoff.propose_niche()
    print("Niche")

def initiation():
    start = input("Do you want 1) select niche or 2) write an article?")

if __name__ == "__main__":
    article()