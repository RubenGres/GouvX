import click
from tqdm import tqdm
from service_public_scraper import ServicePublicScraper
import requests
import os
import json

@click.command()
@click.option('--list', '-l', help='Path of the list of websites to scrape file')
def scrape_links(list):

    with open(list, 'r') as list_file:
        urls = list_file.readlines()
    
    for url in tqdm(urls):
        url = url.strip()

        response = requests.get(url)

        if response.status_code == 200:
            try:
                scraper = ServicePublicScraper(response)
                page_content = scraper.parse_page()
                path = os.path.join("data_scraped", f"{url.split('/')[-1]}.json")

                with open(path, 'w') as f:
                    f.write(json.dumps(page_content))
            except:
                print(url, "HAD AN EXCEPTION")
        else:
            print(url, "ERROR ON REPONSE CODE")

if __name__ == '__main__':
    scrape_links()