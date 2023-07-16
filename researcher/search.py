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
    serpapi_api_key = cfg.serpapi_api_key
except KeyError:
    sys.stderr.write("OpenAI key configuration failed.")
    exit(1)

headers = {'Cache-Control': 'no-cache', 'Content-Type': 'application/json'}
params = {'token': browserless_api_key}

def scrape(link):
    """Scrape the content of a webpage."""
    json_data = {
        'url': link,
        'elements': [{'selector': 'body'}],
    }
    response = requests.post('https://chrome.browserless.io/scrape', params=params, headers=headers, json=json_data)

    if response.status_code == 200:
        webpage_text = response.json()['data'][0]['results'][0]['text']
        return webpage_text
    else:
        return ""

def summarize(question, webpage_text):
    """Summarize the relevant information from a body of text related to a question."""
    prompt = f"""You are an intelligent summarization engine. Extract and summarize the
  most relevant information from a body of text related to a question.

  Question: {question}

  Body of text to extract and summarize information from:
  {webpage_text[0:2500]}

  Relevant information:"""

    response = openai.ChatCompletion.create(
        model=llm_model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    )

    return response.choices[0].message.content


def final_summary(question, summaries):
    """Construct a final summary from a list of summaries."""
    num_summaries = len(summaries)
    prompt = f"You are an intelligent summarization engine. Extract and summarize relevant information from the {num_summaries} points below to construct an answer to a question.\n\nQuestion: {question}\n\nRelevant Information:"

    for i, summary in enumerate(summaries):
        prompt += f"\n{i + 1}. {summary}"

    response = openai.ChatCompletion.create(
        model=llm_model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    )

    return response.choices[0].message.content

def link(r):
    """Extract the link from a search result."""
    return r['link']


def search_results(question):
    """Get search results for a question."""
    search = GoogleSearch({
        "q": question,
        "api_key": serpapi_api_key,
        "logging": False
    })

    result = search.get_dict()
    if 'organic_results' in result:
        return list(map(link, result['organic_results']))
    else:
        print("No organic results found.")
        return []


def print_citations(links, summaries):
    """Print citations for the summaries."""
    print(colorama.Fore.YELLOW + colorama.Style.BRIGHT + "CITATIONS" + colorama.Style.RESET_ALL)
    num_citations = min(len(links), len(summaries))
    for i in range(num_citations):
        print("\n", f"[{i + 1}] {links[i]}\n{summaries[i]}\n")

def go(keyphrase=None):
    if keyphrase is None:
        print(colored("\nWHAT WOULD YOU LIKE ME TO SEARCH?\n", "cyan", attrs=["bold"]))
        keyphrase = input()
    print("\n")
    sys.stdout = open(os.devnull, 'w')  # disable print
    links = search_results(keyphrase)
    sys.stdout = sys.__stdout__  # enable print
    webpages = []
    summaries = []

    # Display progress bar
    with tqdm(total=100, desc="Loading", ncols=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} ", unit=" percent") as pbar:
        for i in range(10):  # Increased from 4 to 10
            if i < len(links):
                webpages.append(scrape(links[i]))
                pbar.update(5)  # Adjusted to accommodate 10 resources
            time.sleep(0.1)
            if i < len(webpages):
                summaries.append(summarize(keyphrase, webpages[i]))
                pbar.update(5)  # Adjusted to accommodate 10 resources

    answer = final_summary(keyphrase, summaries)
    print(colorama.Fore.YELLOW + colorama.Style.BRIGHT + "\n\nHERE IS THE ANSWER\n" + colorama.Style.RESET_ALL)
    print(answer, "\n")
    #print_citations(links, summaries)


if __name__ == "__main__":
    go()