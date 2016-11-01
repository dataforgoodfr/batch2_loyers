# -*- coding: utf-8 -*-

import scrapy, re
from url_scraper.items import GenericItem
from url_scraper.utils import get_sub_area
from geopy.geocoders import Nominatim
from unidecode import unidecode

"""

WWW.PAP.FR

"""


class PapSpider(scrapy.Spider):

    name = "pap_spider"
    custom_settings = {
        'ITEM_PIPELINES' : {'url_scraper.pipelines.PapScraperPipeline': 1,},
        'FEED_FORMAT' : 'json',
        'FEED_URI' : 'output.json',
        'FEED_EXPORTERS' : {'json': 'scrapy.contrib.exporter.JsonItemExporter',}
    }

    def _get_adress(self, item):
        '''
        find adress from geolocator
        '''
        geolocator = Nominatim()
        location = geolocator.reverse(item['coord'])
        return location.address

    def _get_construction_year(self, adress):
        '''
        get construction year from meilleursagents
        '''
        magentsurl = "http://www.meilleursagents.com/prix-immobilier/paris-75000/"

        # load webdriver
        driver = webdriver.Firefox()
        driver.get(magentsurl)
        time.sleep(1)

        # adress input
        textinput = driver.find_element_by_name('q')
        textinput.send_keys(adress)
        time.sleep(1)

        # click input box
        textinput.click()
        time.sleep(1)

        # hit enter
        textinput.send_keys(Keys.RETURN)
        time.sleep(1)

        # get facts
        facts = driver.find_element_by_xpath("//table").text
        time.sleep(1)

        # shut down
        driver.close()

        # dump data
        return facts

    def parse(self, response):
        # scrape apt page
        item = GenericItem()

        # items cleaned in the pipeline
        item['title'] = response.xpath('//span[@class="title"]/text()').extract_first()
        item['price'] = response.xpath('//span[@class="price"]/strong/text()').extract_first()
        item['coord'] = response.xpath('//div[@class="map-annonce-adresse"]/@data-mappy').extract_first()
        item['area'] = response.xpath('//div[@class="item-geoloc"]/h2/text()').extract_first()
        item['url'] = response.url

        # extract text
        item['text'] = response.xpath('//p[@class="item-description"]/text()').extract()
        item['text'] = unidecode(item['text'])

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

        # parse coord / district
        regex = r"[-+]?\d*\.\d+|\d+"
        if item['coord']:
            item['coord'] = map(float, re.findall(regex, item['coord'])[:2])
            item['adress'] = self._get_adress(item)
            # item['construction_year'] = _get_construction_year(item)

        yield item

"""

WWW.SELOGER.COM

"""

class LogSpider(scrapy.Spider):

    name = "selogerCrawler"
    custom_settings = {
        'FEED_FORMAT' : 'json',
        'FEED_URI' : 'output.json',
        'FEED_EXPORTERS' : {'json': 'scrapy.contrib.exporter.JsonItemExporter',}
    }

    def _get_digits(self, line, dtype):
        return dtype(re.findall('\d+', line)[0])

    def parse(self, response):

        item = GenericItem()

        item['ref_n'] = response.xpath("//span[@class='description_ref']/text()").extract_first()
        item['ref_n'] = self._get_digits(item['ref_n'], int)

        item['title'] = response.xpath("//h1[@class='detail-title']/text()").extract()
        item['title'] = re.sub("\n|\r", "", "".join(item['title']))

        item['price'] = response.xpath("//span[@id='price']/text()").extract_first()
        item['price'] = self._get_digits(item['price'], float)

        item['url'] = response.url

        float_re = '\d+[,.]\d+'
        details = response.xpath("//li[contains(@class, 'liste__item')]/text()").extract()

        for detail in details:
            if 'Pi' in detail:
                item['rooms'] = self._get_digits(detail, int)
            elif 'Cham' in detail:
                item['chambre'] = self._get_digits(detail, int)
            elif 'Surf' in detail:
                item['surface'] = float(re.findall(float_re, detail.split(" m2")[0].replace(',','.'))[0])
            elif 'Etage ' in detail:
                item['floor'] = self._get_digits(detail, int)
            elif 'Ter' in detail:
                item['terasse'] = self._get_digits(detail, int)
            elif 'Balc' in detail:
                item['balcon'] = self._get_digits(detail, int)
            elif 'Ann' in detail:
                item['construction_year'] = self._get_digits(detail, int)
            elif 'Charges' in detail:
                item['charges'] = float(re.findall(float_re, detail.replace(',','.'))[0])

            if ' Meubl' in detail:
                item['furn'] = True
            else:
                item['furn'] = False

            if 'elect' in detal:
                item['heat'] = 0
            else:
                item['heat'] = 1

        # get description
        item['text'] = response.xpath("//p[@class='description']/text()").extract()
        item['text'] = unidecode(''.join(item['text']))

        # try to get sub_area from title
        words = item['title'].split()
        item['sub_area'] = get_sub_area(words)

        # if it doesnt work, lookup into the description
        if not item['sub_area']:
            words = item['text'].split()
            item['sub_area'] = get_sub_area(words)

        # agence
        item['agence'] = response.xpath("//h3[@class='agence-title']/text()").extract_first()
        item['agence'] = unidecode(item['agence'])

        # charges
        item['charges']=Selector(response).xpath('//*[@id="%s"]/div/div[2]/div/a/sup/text()'%annonce).extract()[0]

        yield item
