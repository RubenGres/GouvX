import scrapy
from bs4 import BeautifulSoup
import json
import hashlib

import sys
sys.path.append("/workspaces/scrapper")

from scraper import BasicScraper

STARTURL = "https://www.service-public.fr"
OUTPUT_DIR = "/workspaces/data2"

class MySpider(scrapy.Spider):
    name = 'my_spider'

    start_urls = [STARTURL]  # Replace with the initial URL you want to crawl

    def parse(self, response):
        scraper = BasicScraper(response)

        # Use BeautifulSoup manager to parse the page and extract required information
        parsed_data = scraper.parse_page()

        # Process the extracted data as needed (e.g., save it to a file or database)
        self.process_data(parsed_data)

        # Follow links to other pages, if needed
        for next_page_url in scraper.scrape_links(str_filter="service-public.fr"):
            yield response.follow(next_page_url, callback=self.parse)

    def process_data(self, data):
        filename = hashlib.sha256(data['url'].encode('ascii')).hexdigest()
        
        with open(f"{OUTPUT_DIR}/{filename}.json", "w") as outfile:
            json.dump(data, outfile)

        print(data['url'], '->', filename)
