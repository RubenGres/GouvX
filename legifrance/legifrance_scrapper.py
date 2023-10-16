from typing import Any
import scrapy
import unicodedata

from scrapy.http import Response

class LegifranceScrapper(scrapy.Spider):
    name = 'blogspider'
    start_urls = [
        "https://www.legifrance.gouv.fr/liste/code?etatTexte=VIGUEUR"
    ]
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'FEED_EXPORT_ENCODING' : 'utf-8',
        'DOWNLOAD_DELAY': 0.1,
    }

    def parse(self, response):
        
        for elem in response.xpath("//div[@id='main_code']//a[starts-with(text(), 'Code')]"):
            link = elem.xpath("@href").get()
            yield scrapy.Request(response.urljoin(link), callback=self.parse_code)
    
    def parse_code(self, response):
        first_bloc = response.xpath("//a[@class='articleLink' and not(@class='abrogated')]")[0]
        link = first_bloc.xpath("@href").get()
        yield scrapy.Request(response.urljoin(link), callback=self.parse_element)
    
    def parse_element(self, response):
        
        hierarchie = response.xpath("//ul[@id='liste-sommaire-noeud']//a//text()").getall()
        #remove invisible elements (article 1, article 2, etc.)
        hierarchie = [elem for elem in hierarchie if not elem.startswith('\n')]
        
        for article in response.xpath("//article"):
            article_ref = article.css('.name-article:not(.abrogated)').css('::text').get()
            article_url = article.css('.name-article:not(.abrogated)').css('::attr(href)').get()
            
            article_content = article.css('.content:not(.content-abrogated)').css('::text').getall()
            article_content = ''.join(article_content)
            
            if article_content == "":
                continue
            
            # print("saved data: ", article_ref, article_content)
            
            yield {
                'article_ref': article_ref,
                'hierarchie': hierarchie,
                'article_content': article_content,
                'page_title': response.css('title::text').get(),
                'proper_title': f'{hierarchie[0]} > {article_ref}',
                'url': article_url,
                'subdomain': 'legifrance',
                'domain': 'gouv.fr'
            }
            
        
        suivant_url = response.css('#urlNextSection::attr(href)').get()
        suivant_url = "https://www.legifrance.gouv.fr" + suivant_url
        
        if suivant_url:
            yield scrapy.Request(response.urljoin(suivant_url), callback=self.parse_element)