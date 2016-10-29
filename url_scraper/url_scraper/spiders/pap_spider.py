import scrapy, re
from url_scraper.items import GenericItem
from geopy.geocoders import Nominatim

class PapSpider(scrapy.Spider):
    name = "pap_spider"
    custom_settings = {
        'ITEM_PIPELINES' : {'url_scraper.pipelines.PapScraperPipeline': 1,},
        'FEED_FORMAT' : 'json',
        'FEED_URI' : 'output.json',
        'FEED_EXPORTERS' : {'json': 'scrapy.contrib.exporter.JsonItemExporter',}
    }

    def parse(self, response):
        # scrape apt page
        item = GenericItem()

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

        # parse coord / district
        regex = r"[-+]?\d*\.\d+|\d+"
        if item['coord']:
            item['coord'] = map(float, re.findall(regex, item['coord'])[:2])
            item['adress'] = self.get_adress(item)
            # item['construction_year'] = get_construction_year(item)

        yield item

    def get_adress(self, item):
        # find adress from geolocator
        geolocator = Nominatim()
        location = geolocator.reverse(item['coord'])
        return location.address

    def get_construction_year(self, adress):
        # find construction_year from meilleursagents
        magentsurl = "http://www.meilleursagents.com/prix-immobilier/paris-75000/"

        # load webdriver
        driver = webdriver.Firefox()
        driver.get(magentsurl)
        time.sleep(1)

        # adress input
        textinput = driver.find_element_by_name('q')
        textinput.send_keys("3, rue veronese")
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
