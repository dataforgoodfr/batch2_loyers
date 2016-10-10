import scrapy, re
from pap_scraper.items import PapScraperItem
from scrapy.shell import inspect_response

class PapSpider(scrapy.Spider):
    name = "pap_spider"
    base_url = "http://www.pap.fr/annonce/locations-appartement-paris-75-g439-"
    start_urls = [base_url + "entre-300-et-700-euros",
                  base_url + "entre-700-et-850-euros",
                  base_url + "entre-850-et-1000-euros",
                  base_url + "entre-1000-et-1250-euros",
                  base_url + "entre-1250-et-1500-euros",
                  base_url + "entre-1500-et-1750-euros",
                  base_url + "entre-1750-et-3000-euros",
                  base_url + "entre-3000-et-7000-euros", ]

    def parse(self, response):
        # starts from the locations + paris search result page
        # then makes a list of all links on the page
        href_list = response.css('a[class="title-item"]::attr(href)').extract()
        for href in href_list:
            yield scrapy.Request(response.urljoin(href),
                                 callback=self.parse_apts)

        # get to the next menu (until no items left)
        next_page = response.css('li.next a::attr(href)').extract_first()
        if next_page is not None:
            yield scrapy.Request(response.urljoin(next_page),
                                 callback=self.parse)

    def parse_apts(self, response):
        # scrape apt page
        item = PapScraperItem()

        # cleaning -> pipeline
        item['title'] = response.xpath('//span[@class="title"]/text()').extract_first()
        item['price'] = response.xpath('//span[@class="price"]/strong/text()').extract_first()
        item['coord'] = response.xpath('//div[@class="map-annonce-adresse"]/@data-mappy').extract_first()
        item['area'] = response.xpath('//div[@class="item-geoloc"]/h2/text()').extract_first()
        item['text'] = response.xpath('//p[@class="item-description"]/text()').extract()
        item['url'] = response.url

        # ref is collided with date -> pipeline
        item['ref_n'] = response.xpath('//p[@class="date"]/text()').extract_first()

        # surface is collided with n_rooms -> pipeline
        summary = response.xpath('//ul[@class="item-summary"]//li')
        for elem in summary:
            text = elem.xpath('strong/text()').extract_first()
            if 'Pi' in elem.extract():
                item['rooms'] = int(text)
            if 'Su' in elem.extract():
                item['surface'] = text
            if 'Ch' in elem.extract():
                item['bedrooms'] = int(text)

        yield item
