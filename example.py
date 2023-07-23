from scraper import SoupScraper

scrapper = SoupScraper()

target = 'https://www.agriculture.gouv.fr'  # Replace with the desired URL

print(scrapper.scrape_text(target))
