import sys
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from bs4 import BeautifulSoup
import json
import hashlib
import re
import os
from pathlib import Path

from service_public_scraper import BasicScraper


OUTPUT_DIR = "_scraped" # specify the path of the output dir here


def get_path_from_url(url):
    """
        (ex. url1.gouv.fr/page/scraped -> fr/gouv/url1/page/scraped.json)
    """

    # Remove the "https://" or "http://" prefix from the URL
    url_without_protocol = re.sub(r'^https?://', '', url)

    # Split the remaining URL into parts using "/" as the separator
    url_parts = url_without_protocol.split('/')
    # Remove empty parts (e.g., if the URL ends with a '/')
    url_parts = [part for part in url_parts if part]

    first_parts = url_parts[0].split('.')
    first_parts.reverse()
    begin_path = '/'.join(first_parts)

    second_part = url_parts[1:]
    if second_part == []:
        second_part = ['_root']

    rest_of_path = '/'.join(second_part) + '.json'

    # Join the URL parts using '/' to create the desired file path
    file_path = begin_path + '/' + rest_of_path

    return file_path


class ServicePublicScraper(scrapy.Spider):
    name = 'service_public'

    start_urls = ["https://www.service-public.fr"]  # Replace with the initial URL you want to crawl
    allowed_domains=["service-public.fr"]
    rules = (
        Rule(LinkExtractor(deny=(r"lannuaire\.service-public\.fr",)))
    )

    def parse(self, response):
        scraper = BasicScraper(response)

        # Use BeautifulSoup manager to parse the page and extract required information
        parsed_data = scraper.parse_page()

        # Process the extracted data as needed (e.g., save it to a file or database)
        self.process_data(parsed_data)

        # Follow links to other pages, if needed
        for next_page_url in scraper.scrape_links(include="service-public\.fr", exclude=r"lannuaire\.service-public\.fr"):
            yield response.follow(next_page_url, callback=self.parse)


    def process_data(self, data):
        #filename = hashlib.sha256(data['url'].encode('ascii')).hexdigest()
        filename = get_path_from_url(data["url"])
        full_filename = f"{OUTPUT_DIR}/{filename}"

        os.makedirs(Path(full_filename).parent, exist_ok=True)
        
        with open(full_filename, "w") as outfile:
            json.dump(data, outfile)