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
        'FEED_EXPORTERS' : {'json': 'scrapy.contrib.exporter.JsonItemExporter',},
        'USER_AGENT':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'
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
        'FEED_EXPORTERS' : {'json': 'scrapy.contrib.exporter.JsonItemExporter',},
        'USER_AGENT':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'
    }

    def _get_digits(self, line, dtype):
        return dtype(re.findall('\d+', line)[0])

    def parse(self, response):

        item = GenericItem()

        item['ref_n'] = response.xpath("//span[@class='description_ref']/text()").extract_first()
        item['ref_n'] = self._get_digits(item['ref_n'], int)

        item['title'] = response.xpath("//h1[@class='detail-title']/text()").extract()
        item['title'] = re.sub("\n|\r", " ", "".join(item['title']))
        item['title'] = unidecode(''.join(item['title']))

        item['price'] = response.xpath("//span[@id='price']/text()").extract_first()
        item['price'] = self._get_digits(item['price'], float)

        latitude = response.xpath("//*[@id='resume__map_new']/@data-coordonnees-latitude").extract_first()
        longitude = response.xpath("//*[@id='resume__map_new']/@data-coordonnees-longitude").extract_first()
        ne_latitude = response.xpath("//*[@id='resume__map_new']/@data-boudingbox-northeast-latitude").extract_first()
        ne_longitude = response.xpath("//*[@id='resume__map_new']/@data-boudingbox-northeast-longitude").extract_first()
        sw_latitude = response.xpath("//*[@id='resume__map_new']/@data-boudingbox-southwest-latitude").extract_first()
        sw_longitude = response.xpath("//*[@id='resume__map_new']/@data-boudingbox-southwest-longitude").extract_first()

        if latitude:
            item['coord'] = [float(latitude), float(longitude)]
        else:
            latitude = (float(ne_latitude) + float(sw_latitude)) / 2.
            longitude = (float(ne_longitude) + float(sw_longitude)) / 2.
            item['coord'] = [latitude, longitude]

        item['url'] = response.url

        details = response.xpath("//li[contains(@class, 'liste__item')]/text()").extract()

        for detail in details:
            if 'Pi' in detail:
                item['rooms'] = self._get_digits(detail, int)
            elif 'Cham' in detail:
                print detail
                item['bedrooms'] = self._get_digits(detail, int)
            elif 'Surf' in detail:
                item['surface'] = self._get_digits(detail, float)
            elif 'Etage ' in detail:
                item['floor'] = self._get_digits(detail, int)
            elif 'Ter' in detail:
                item['terasse'] = self._get_digits(detail, int)
            elif 'Balc' in detail:
                item['balcon'] = self._get_digits(detail, int)
            elif 'Ann' in detail:
                item['construction_year'] = self._get_digits(detail, int)
            elif 'Charges' in detail:
                item['charges'] = self._get_digits(detail, float)

            if ' Meubl' in detail:
                item['furn'] = True
            else:
                item['furn'] = False

            if 'elect' in detail:
                item['heat'] = 0
            else:
                item['heat'] = 1

        # get description
        item['text'] = response.xpath("//p[@class='description']/text()").extract()
        item['text'] = re.sub("\n|\r", " ", "".join(item['text']))
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
        item['agence'] = re.sub("\n|\r", " ", "".join(item['agence']))
        item['agence'] = unidecode(item['agence'])

        yield item
