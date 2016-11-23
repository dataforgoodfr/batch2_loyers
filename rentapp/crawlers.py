# -*- coding: utf-8 -*-

import re, datetime, requests
from lxml import html
from geopy.geocoders import Nominatim
from unidecode import unidecode
from utils.inside_quarters import get_quarter

class BasicItem(object):

    def __init__(self, url):
        self.status = None
        self.tree = None
        self.item = {
            'url' : url,
            'scrap_date' : None,
            'title' : None,
            'rent_cc' : None,
            'rent_nc' : None,              # needed
            'charges' : None,
            'coord' : None,
            'area' : None,
            'sub_area' : None,             # needed
            'desc' : None,
            'refnumber' : None,
            'details' : None,
            'rooms' : None,
            'surface' : None,              # needed
            'bedrooms' : None,
            'agence' : None,
            'address' : None,
            'construction_year' : None,    # needed
            'floor' : None,
            'terrace' : None,
            'balcony' : None,
            'furnitures' : None,           # needed
        }

class PapCrawler(BasicItem):
    
    def __init__(self, url):
        BasicItem.__init__(self, url)
        self.starttime = datetime.datetime.now()

    def get_tree(self):
        headers = {'user-agent': 'my-app/0.0.1'}
        response = requests.get(self.item['url'], headers=headers)
        self.tree = html.fromstring(response.text)
        self.status = response.status_code

    def get_item(self):

        selectors = {
            'title' : '//span[@class="title"]/text()',
            'rent_cc' : '//span[@class="price"]/strong/text()',
            'coord' : '//div[@class="map-annonce-adresse"]/@data-mappy',
            'area' : '//div[@class="item-geoloc"]/h2/text()',
            'desc' : '//p[@class="item-description"]/text()',
            'refnumber' : '//p[@class="date"]/text()',
            'details' : '//ul[@class="item-summary"]//li',
        }

        # select raw data into html
        for key, selector in selectors.items():
            self.item[key] = self.tree.xpath(selector)

        # parse the details section
        for elem in self.item['details']:
            text = elem.xpath('strong/text()')
            
            if 'Pi' in elem.text:
                self.item['rooms'] = text[0]
            if 'Su' in elem.text:
                self.item['surface'] = text[0]
            if 'Ch' in elem.text:
                self.item['bedrooms'] = text[0]

        # meublé
        if 'eubl' in self.item['title']:
            item['furnitures'] == True
        else:
            item['furnitures'] == False

        # extract sub_area / address and coordinates
        geolocator = Nominatim()
        regex = r"[-+]?\d*\.\d+|\d+"
        raw_coord = str(self.item['coord'][0])
        str_coord = re.findall(regex, raw_coord)[:2]
        clean_coord = [float(x) for x in str_coord]
        self.item['address'] = geolocator.reverse(clean_coord).address
        self.item['sub_area'] = get_quarter(clean_coord)
        self.item['coord'] = clean_coord

    def clean_item(self, item):

        def text_to_unicode(text):
            return unidecode(text)

        def remove_spaces(text):
            return re.sub(r'[\n\r\t]', ' ', text)

        def get_digits(text, dtype):
            return dtype(''.join(re.findall('\d+', text)))

        # formatting
        item['desc'] = ''.join(item['desc'])
        item['title'] = ''.join(item['title'])
        item['area'] = str(item['area'][0])
        item['rent_cc'] = get_digits(item['rent_cc'][0], float)
        item['surface'] = get_digits(item['surface'], float)

        # format reference
        regex = r'(?<=: ).*?(?= / )'
        raw_ref = str(item['refnumber'][0])
        matches = re.search(regex, raw_ref)
        item['refnumber'] = matches.group()
        
        # cleaning
        for key, attr in item.items():
            if type(attr) == str:
                item[key] = text_to_unicode(attr)
                item[key] = remove_spaces(attr)

        del(item['details'])

        return item

    def run(self):
        self.get_tree()
        self.get_item()
        self.item = self.clean_item(self.item)
        self.now = datetime.datetime.now()
        self.item['scrap_date'] = self.now
        self.scraping_time = datetime.datetime.now() - self.starttime

#############################SELOGER#################################

class SeLogerCrawler(BasicItem):
    
    def __init__(self, url):
        BasicItem.__init__(self, url)
        self.starttime = datetime.datetime.now()

    def get_tree(self):
        headers = {'user-agent': 'my-app/0.0.7'}
        response = requests.get(self.item['url'], headers=headers)
        self.tree = html.fromstring(response.text)
        self.status = response.status_code

    def get_item(self):

        selectors = {
            'title' : '//h1[@class="detail-title"]/text()',
            'rent_cc' : '//span[@id="price"]',
            'coord' : '//div[@class="map-annonce-adresse"]/@data-mappy',
            'area' : '//h2[@class="detail-subtitle"]/span/text()',
            'desc' : '//p[@class="description"]/text()',
            'refnumber' : '//span[@class="description_ref"]/text()',
            'details' : '//li[contains(@class, "liste__item")]/text()',
            'agence' : '//h3[@class="agence-title"]/text()'
        }

        for key, selector in selectors.items():
            self.item[key] = self.tree.xpath(selector)

    def parse_details(self):

        def get_digits(text, dtype):
            text = text.replace(',', '.')
            return dtype(''.join(re.findall('\d+', text)))
        
        for detail in self.item['details']:
            
            if 'Pi' in detail:
                self.item['rooms'] = get_digits(detail, int)
            elif 'Cham' in detail:
                self.item['bedrooms'] = get_digits(detail, int)
            elif 'Surf' in detail:
                self.item['surface'] = get_digits(detail, float)
            elif 'Etage ' in detail:
                self.item['floor'] = get_digits(detail, int)
            elif 'Ter' in detail:
                self.item['terrace'] = get_digits(detail, int)
            elif 'Balc' in detail:
                self.item['balcony'] = get_digits(detail, int)
            elif 'Ann' in detail:
                self.item['construction_year'] = get_digits(detail, int)
            elif 'Charges' in detail:
                self.item['charges'] = get_digits(detail, float)

            if ' Meubl' in detail:
                self.item['furnitures'] = True
            else:
                self.item['furnitures'] = False

            if 'elect' in detail:
                self.item['heat'] = 0
            else:
                self.item['heat'] = 1

        # get coordinates
        geocodes = {
            'lat' : "//*[@id='resume__map_new']/@data-coordonnees-latitude",
            'lon' : "//*[@id='resume__map_new']/@data-coordonnees-longitude",
            'ne_lat' : "//*[@id='resume__map_new']/@data-boudingbox-northeast-latitude",
            'ne_lon' : "//*[@id='resume__map_new']/@data-boudingbox-northeast-longitude",
            'sw_lat' : "//*[@id='resume__map_new']/@data-boudingbox-southwest-latitude",
            'sw_lon' : "//*[@id='resume__map_new']/@data-boudingbox-southwest-longitude"
        }

        for key, selector in geocodes.items():
            raw_coord = self.tree.xpath(selector)[0]
            if raw_coord:
                geocodes[key] = float(raw_coord)

        if type(geocodes['lat']) == float:
            coordinates = [geocodes['lat'], geocodes['lon']]
        else:
            latitude = (geocodes['ne_lat'] + geocodes['sw_lat']) / 2.
            longitude = (geocodes['ne_lon'] + geocodes['sw_lon']) / 2.
            coordinates = [latitude, longitude]

        # get adress / sub_area
        geolocator = Nominatim()
        self.item['coord'] = coordinates
        self.item['address'] = geolocator.reverse(coordinates).address
        self.item['sub_area'] = get_quarter(coordinates)

        # check that charges are included
        rent_type = self.item['rent_cc'][0].xpath('//sup')[0].text
        raw_rent = get_digits(self.item['rent_cc'][0].text, float)
        
        if 'CC' in rent_type:
            self.item['rent_cc'] = raw_rent
            if self.item['charges']:
                self.item['rent_nc'] = raw_rent - self.item['charges']
        else:
            self.item['rent_nc'] = raw_rent
            if self.item['charges']:
                self.item['rent_cc'] = raw_rent + self.item['charges']

    def clean_item(self):

        def text_to_unicode(text):
            return unidecode(text)

        def remove_spaces(text):
            return re.sub(r'[\n\r\t]', ' ', text)

        # formatting
        self.item['desc'] = str(self.item['desc'][0])
        self.item['area'] = str(self.item['area'][0])
        self.item['title'] = str(self.item['title'][0])
        self.item['agence'] = str(self.item['agence'][0])

        # cleaning
        for key, attr in self.item.items():
            if type(attr) == str:
                self.item[key] = text_to_unicode(attr)
                self.item[key] = remove_spaces(attr)

        del(self.item['details'])

    def run(self):
        self.get_tree()
        self.get_item()
        self.parse_details()
        self.clean_item()
        self.now = datetime.datetime.now()
        self.item['scrap_date'] = self.now
        self.scraping_time = datetime.datetime.now() - self.starttime