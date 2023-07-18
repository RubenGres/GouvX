import requests
from bs4 import BeautifulSoup


class SoupScraper:
    def __init__(self):
        self.soups = {}

    def reformat_link(self, link, url):
        if link[0] == '/':
            return url + link

        if link.startswith("http"):
            return link
        
        return 'http://' + link

    def get(self, url):
        if url in self.soups:
            return self.soups[url]

        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.soups[url] = soup

        return soup
    
    
    def scrape_text(self, url):
        soup = self.get(url)
        text_content = soup.get_text()
        return text_content
    

    def scrape_links(self, url):
        soup = self.get(url)

        link_tags = soup.find_all('a')
        
        # Extract the URLs from the <a> tags
        links = []
        for link_tag in link_tags:
            link = link_tag.get('href')
            if link:
                links.append(link)

        links = list(filter(lambda x: '#' not in x, links))

        links = list(set([self.reformat_link(l, url) for l in links]))

        return links
    
    
    def scrape_img_url(self, url):
        soup = self.get(url)

        img_tags = soup.find_all('img')
        
        # Extract the URLs from the <a> tags
        imgs = []
        for img_tag in img_tags:
            img = img_tag.get('src')
            
            if img:
                imgs.append(self.reformat_link(img, url))

        return imgs


    def get_headers(self, url):
        response = requests.head(url)
        return response.headers
