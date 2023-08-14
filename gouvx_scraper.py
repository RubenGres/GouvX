import requests
from bs4 import BeautifulSoup
import re

class BasicScraper:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, 'html.parser')
        self.url = response.url

    def reformat_link(self, link):
        if link[0] == '/':
            return self.url + link

        if link.startswith("http"):
            return link
        
        return 'http://' + link
    

    def scrape_text(self):
        text_content = self.soup.get_text()
        return text_content
    

    def scrape_links(self, include=None, exclude=None):
        link_tags = self.soup.find_all('a')
        
        # Extract the URLs from the <a> tags
        links = []
        for link_tag in link_tags:
            link = link_tag.get('href')
            if link:
                links.append(link)

        links = list(filter(lambda x: '#' not in x, links))
        links = list(set([self.reformat_link(l) for l in links]))

        links = [link.split('?')[0] for link in links]

        if include:
            pattern = re.compile(include)
            links = [link for link in links if pattern.search(link)]

        if exclude:
            pattern = re.compile(exclude)
            links = [link for link in links if not pattern.search(link)]

        return links
    
    def scrape_img_url(self):
        img_tags = self.soup.find_all('img')
        
        # Extract the URLs from the <a> tags
        imgs = []
        for img_tag in img_tags:
            img = img_tag.get('src')
            
            if img:
                imgs.append(self.reformat_link(img))

        return imgs

    def get_headers(self):
        response = requests.head(self.url)
        return response.headers

    def parse_page(self):
        return {
            "url": self.url,
            "text": self.scrape_text(),
            #"body": self.response.text,
            "images": self.scrape_img_url(),
            "links": self.scrape_links()
        }
    