import requests
from bs4 import BeautifulSoup
import re

def parse_table(table):
    output = "\n\n"
    rows = table.find_all('tr')

    for i, row in enumerate(rows):
        cells = row.find_all(['th', 'td'])
        cell_texts = [cell.get_text(strip=True) for cell in cells]

        if i == 0:
            output += "|" + "|".join(cell_texts) + "|\n"  # Header row
            output += "|" + "|".join(["---"] * len(cells)) + "|\n"  # Separator row
        else:
            output += "|" + "|".join(cell_texts) + "|\n"  # Data rows
        
    return output


def parse_link(link):
    link_text = link.get_text()
    link_url = link.get('href')
    return f'[{link_text}]({link_url})'


def parse_element(element):
    # Initialize an empty string to store the result
    output = ""

    elements = [element] if not isinstance(element, list) else element

    for elem in elements:
        if hasattr(elem, "children"):
            # Recursively process children
            child_output = parse_element(list(elem.children))
            if elem.name and len(elem.name) == 2 and elem.name.startswith('h'):
                header_level = int(elem.name[1])
                output += f'\n\n{"#" * header_level} {child_output}:\n'
            elif elem.name == 'li':
                output += f'\n- {child_output}'
            elif elem.name == 'p':
                output += f'\n{child_output}'
            elif elem.name == "strong":
                if len(list(elem.parent.children)) == 1 and elem.parent.name == "p" and elem.get_text() == elem.parent.get_text():
                    output += f'\n##### {child_output}'
                else:
                    output += elem.get_text()
            elif elem.name == 'table':
                output += parse_table(elem)
            elif elem.name == 'a':
                output += parse_link(elem)
            else:
                output += child_output
        else:
            # Base case: If there are no children, just append the text
            output += elem.get_text()
    
    return output


def get_tabs(soup):
    main_div = soup.find('main', id='main')
    article = main_div.find('article')
    fiche = article.find('div', id="expired", attrs={"data-test": "div-content-fiche"})
        
    tabs = fiche.select('[id^="main-tabs-situation-content-"], [data-toggle-scope-seeall="chapters"]')
    
    if not tabs:
        text_content = fiche

        return zip(['']*len(text_content), text_content)

    tab_header = fiche.find(class_="fr-tabs__list")
    if tab_header:
        tab_names = [f'#{name.get_text()}\n\n' for name in tab_header.find_all('li')]
        return zip(tab_names, tabs)
    else:
        return zip([''], tabs)



def parse_tabs(tab):
    output = ""
    
    chapters = tab.find_all('div', class_="sp-chapter")

    if not chapters:
        output += parse_element(tab)
        output += '\n\n\n'
    else:
        for chapter in chapters:
            output += parse_chapter(chapter)
            output += '\n\n\n'

    return output


def get_metadata(soup):
    main_div = soup.find('main', id='main')
    nav = main_div.find('nav').find('ol').find_all('li')
    breadcrums = [n.get_text() for n in nav]

    article = main_div.find('article')

    title = article.find('h1').get_text()
    date_verif = article.find('p',  attrs={"data-test": "date-maj"}).get_text().split(' - ')[0]
    
    intro = article.find('div', id='intro')
    intro = parse_element(intro) if intro else None

    return {
        "breadcrums": breadcrums,
        "title": title,
        "date_verif": date_verif,
        "intro": intro
    }


def parse_chapter(chapter):
    output = ""

    chapter_title = chapter.find(class_='sp-chapter-title').get_text()
    output += f'##{chapter_title}\n'

    chapter_content = chapter.find("div", class_="sp-chapter-content")
    output += parse_element(chapter_content)

    return output


def trim_bottom(text):
    return text.split("## Cette page vous a-t-elle été utile")[0]


class ServicePublicScraper:
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
    

    def scrape_text(self, trim=True):
        output = ""

        for tab_title, tab_content in get_tabs(self.soup):
            output += f'{tab_title}'
            for tab_text in parse_tabs(tab_content):
                output += tab_text

        if trim:
            output = trim_bottom(output)

        return output
    

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
        metadata = get_metadata(self.soup)

        return {
            "url": self.url,
            "title": metadata["title"],
            "breadcrums": metadata["breadcrums"],
            "intro": metadata["intro"],
            "date_verif": metadata["date_verif"],
            "text": self.scrape_text(),
            "images": self.scrape_img_url(),
            "links": self.scrape_links()
        }
    