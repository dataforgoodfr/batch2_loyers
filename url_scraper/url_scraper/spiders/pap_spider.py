import scrapy, re
from url_scraper.items import GenericItem
from geopy.geocoders import Nominatim

class PapSpider(scrapy.Spider):
    name = "pap_spider"
    custom_settings = {
        'ITEM_PIPELINES': {'url_scraper.pipelines.PapScraperPipeline': 1,}
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
            # extract coord
            item['coord'] = map(float, re.findall(regex, item['coord'])[:2])
            # find adress
            geolocator = Nominatim()
            location = geolocator.reverse(item['coord'])
            item['adress'] = location.address
            # try to get the year of construction
            ma_url = 'http://www.meilleursagents.com/prix-immobilier/paris-75000/'
            request = scrapy.http.FormRequest(url=ma_url,
                                          formdata={'q': item['adress']},
                                          callback=self.after_search)
            request.meta['item'] = item
            yield request
        yield item

    def after_search(self, response):
        item = response.meta['item']
        item['construction_year'] = response.xpath("//table[@class='facts']/text()")
        yield item
