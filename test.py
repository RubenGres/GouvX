from gouvx_scraper import ServicePublicScraper
import requests

url = "https://www.service-public.fr/particuliers/vosdroits/F929"
url = "https://www.service-public.fr/particuliers/vosdroits/F168"
response = requests.get(url)
scraper = ServicePublicScraper(response)
page_content = scraper.parse_page()

#print(page_content['text'])

with open('page_test.md', 'w') as f:
    f.write(page_content['text'])