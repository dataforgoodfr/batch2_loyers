# -*- coding: utf-8 -*-

import re, datetime, requests, string
from lxml import html
from unidecode import unidecode
from utils.tools import get_quarter, fuzz_quarter, get_year, fuzz_word

# UTILS

def get_digits(text, dtype):
    return dtype(''.join(re.findall('\d+', text)))

def remove_spaces(text):
    return re.sub(r'[\n\r\t]', ' ', text)

def text_to_unicode(text):
    return unidecode(text)

def remove_punctuation(text):
    translator = str.maketrans({key: ' ' for key in string.punctuation})
    return text.translate(translator)

# ERRORS

class ParsingError(Exception):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "Couldn't parse %s" %self.name

class FormattingError(Exception):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "Couldn't format %s" %self.name

class ConnexionError(Exception):
    def __str__(self):
        return "Couldn't not reach advert"

class ExpirationError(Exception):
    def __str__(self):
        return "Advert has expired"

# PAP SCRAPER

class PapCrawler(object):

    def __init__(self, url):
        self.start = datetime.datetime.now()
        self.url = url
        self.get_html()
        self.parse_html()
        self.get_title()
        self.get_ref()
        self.get_description()
        self.get_coord()
        self.get_furnitures()
        self.get_area()
        self.get_subarea()
        self.get_details()
        self.get_surface()
        self.get_rooms()
        self.get_year()
        self.get_price()
        self.get_heating()
        self.get_energy()
        self.get_lift()
        self.get_gardien()
        self.get_internet()
        self.close()

    def get_html(self):
        response = requests.get(self.url, headers='')
        if response.status_code != 200:
            raise ConnexionError()
        if 'expiree' in response.url:
            raise ExpirationError()
        self.response = response

    def parse_html(self):
        self.html = html.fromstring(self.response.text)

    def get_title(self):
        selector = '//span[@class="title"]/text()'
        title = self.html.xpath(selector)
        title = ''.join(title)
        title = remove_spaces(title)
        assert type(title) == str
        self.title = title

    def get_ref(self):
        selector = '//p[@class="date"]/text()'
        raw_ref = str(self.html.xpath(selector)[0])
        regex = r'(?<=: ).*?(?= / )'
        matches = re.search(regex, raw_ref)
        ref = ''.join(matches.group())
        assert type(ref) == str
        self.ref = ref

    def get_description(self):
        selector = '//p[@class="item-description"]/text()'
        raw_description = self.html.xpath(selector)
        description = ''.join(raw_description)
        assert type(description) == str
        description = remove_spaces(description)
        description = text_to_unicode(description)
        description = remove_punctuation(description)
        self.description = description

    def get_coord(self):
        try:
            selector = '//div[@class="map-annonce-adresse"]/@data-mappy'
            raw_coord = str(self.html.xpath(selector)[0])
            regex = r"[-+]?\d*\.\d+|\d+"
            str_coord = re.findall(regex, raw_coord)[:2]
            clean_coord = [float(x) for x in str_coord]
            assert type(clean_coord) == list
            assert len(clean_coord) == 2
            self.coord = clean_coord
            self.coord_method = 'exact'
        except:
            # if no coord try fuzzy matching later
            self.coord = None
            self.coord_method = 'no_data'

    def get_furnitures(self):
        assert type(self.title) == str
        if 'eubl' in self.title:
            self.furnitures = 1
        else:
            self.furnitures = 0

    def get_area(self):
        selector = '//div[@class="item-geoloc"]/h2/text()'
        raw_area = self.html.xpath(selector)[0]
        self.area = int(re.findall('\d+', raw_area)[0])
        assert type(self.area) == int

    def get_subarea(self):
        if self.coord:
            result = get_quarter(self.coord)
            assert type(result) == dict
            self.subarea = result['quarter']
            # self.area = int(result['area'])
        else:
            # try fuzzy matching
            self.subarea = fuzz_quarter(self.description) 

    def get_details(self):
        selector = '//ul[@class="item-summary"]//li'
        details = self.html.xpath(selector)
        self.details = details

    def get_surface(self):
        for detail in self.details:
            text = detail.xpath('strong/text()')
            if 'Su' in detail.text:
                surface = text[0]
        surface = get_digits(surface, int)
        assert type(surface) == int
        self.surface = surface

    def get_rooms(self):
        rooms = 0
        bedrooms = 0
        for detail in self.details:
            text = detail.xpath('strong/text()')
            if 'Pi' in detail.text:
                rooms = get_digits(text[0], int)
            if 'Ch' in detail.text:
                bedrooms = get_digits(text[0], int)
        # rooms and bedrooms make no difference
        # for the algorithm.
        rooms = rooms + bedrooms
        assert type(rooms) == int
        self.rooms = rooms

    def get_year(self):
        results = get_year(self.coord, self.subarea, self.area)
        self.year_method = results['method']
        self.year = results['year']

    def get_price(self):
        selector = '//span[@class="price"]/strong/text()'
        raw_price = self.html.xpath(selector)[0]
        price = get_digits(raw_price, int)
        assert type(price) == int
        self.price = price # minus charges

    def get_heating(self):
        words = 'collectif'
        result = fuzz_word(self.description, words)
        if result:
            self.heating = 'collective'
        else:
            # default value
            self.heating = 'individuel'

    def get_energy(self):
        words = ['fuel', 'gaz', 'electricite']
        energy = {}
        for w in words:
            energy[w] = fuzz_word(self.description, w)
        self.energy = energy

    def get_lift(self):
        words = 'sans ascenseur'
        result = fuzz_word(self.description, words)
        if result:
            self.lift = 0
        else:
            words = 'ascenseur'
            result = fuzz_word(self.description, words)
            if result:
                self.lift = 1
            else:
                self.lift = 0

    def get_gardien(self):
        words = 'gardien'
        result = fuzz_word(self.description, words)
        if result:
            self.gardien = 1
        else:
            # default value
            self.gardien = 0

    def get_internet(self):
        words = 'internet'
        result = fuzz_word(self.description, words)
        if result:
            self.internet = 1
        else:
            # default value
            self.internet = 0        

    def close(self):
        del(self.html, self.response, 
            self.title, self.details)
        end = datetime.datetime.now()
        self.scraping_time = str(end - self.start)
        self.start = str(self.start) # str because json


# SE LOGER

class SeLogerCrawler(object):

    def __init__(self, url):
        self.start = datetime.datetime.now()
        self.url = url
        self.get_html()
        self.parse_html()
        self.get_title()
        self.get_ref()
        self.get_coord()
        self.get_details()
        self.get_furnitures()
        self.get_subarea()
        self.get_price()
        self.get_charges()
        self.get_surface()
        self.get_year()
        self.close()

    def get_html(self):
        response = requests.get(self.url, headers='')
        if response.status_code != 200:
            raise ConnexionError()
        if 'expiree' in response.url:
            raise ExpirationError()
        self.response = response

    def parse_html(self):
        self.html = html.fromstring(self.response.text)

    def get_title(self):
        selector = '//h1[@class="detail-title"]/text()'
        title = self.html.xpath(selector)
        title = ''.join(title)
        title = remove_spaces(title)
        assert type(title) == str
        self.title = title

    def get_ref(self):
        selector = '//span[@class="description_ref"]/text()'
        raw_ref = str(self.html.xpath(selector)[0])
        ref = get_digits(raw_ref, str)
        assert type(ref) == str
        self.ref = ref

    def get_coord(self):
        base = "//*[@id='resume__map_new']/@data-"
        codes = {
            'lat' : "".join([base, "coordonnees-latitude"]),
            'lon' : "".join([base, "coordonnees-longitude"]),
            'ne_lat' : "".join([base, "boudingbox-northeast-latitude"]),
            'ne_lon' : "".join([base, "boudingbox-northeast-longitude"]),
            'sw_lat' : "".join([base, "boudingbox-southwest-latitude"]),
            'sw_lon' : "".join([base, "boudingbox-southwest-longitude"]),
        }

        for key, selector in codes.items():
            raw_coord = self.html.xpath(selector)[0]
            if raw_coord:
                codes[key] = float(raw_coord)

        if type(codes['lat']) == float:
            coord = [codes['lat'], codes['lon']]
            self.coord_method = 'exact'
        else:
            latitude = (codes['ne_lat'] + codes['sw_lat']) / 2.
            longitude = (codes['ne_lon'] + codes['sw_lon']) / 2.
            coord = [latitude, longitude]
            self.coord_method = 'center'

        assert type(coord) == list
        assert len(coord) == 2
        self.coord = coord

    def get_details(self):
        selector = '//li[contains(@class, "liste__item")]/text()'
        details = self.html.xpath(selector)
        assert type(details) == list
        self.details = details

    def get_furnitures(self):
        for detail in self.details:
            if ' Meubl' in detail:
                self.furnitures = True
            else:
                self.furnitures = False

    def get_subarea(self):
        subarea = get_quarter(self.coord)
        assert type(subarea) == str
        self.subarea = subarea

    def get_price(self):
        selector = '//span[@id="price"]'
        raw_price = self.html.xpath(selector)[0]
        price = get_digits(raw_price.text, float)
        
        text = raw_price.xpath('//sup')[0].text # check for charges included
        if 'CC' in text:
            self.charges_included = True
        else:
            self.charges_included = False
        assert type(price) == float
        assert type(self.charges_included) == bool
        self.price = price

    def get_charges(self):
        charges = None
        for detail in self.details:
            if 'Charges' in detail:
                charges = get_digits(detail, float)
        if not charges:
            if not self.charges_included:
                # insert prediction
                charges = 1.0
        assert type(charges) == float
        self.charges = charges

    def get_surface(self):
        for detail in self.details:
            if 'Surf' in detail:
                surface = get_digits(detail, float)
        assert type(surface) == float
        self.surface = surface

    def get_year(self):
        year = None
        for detail in self.details:
            if 'Ann' in detail:
                year = get_digits(detail, int)
                self.year_method = 'details'
                self.year = year
        if not year:
            results = get_year(self.coord, self.subarea, 
                               method=self.coord_method)
            self.year_method = results['method']
            self.year = results['year']
        assert type(self.year) == int

    def close(self):
        del(self.html, self.response, 
            self.details, self.title)
        end = datetime.datetime.now()
        self.scraping_time = end - self.start