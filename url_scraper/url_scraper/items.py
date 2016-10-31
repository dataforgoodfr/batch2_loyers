# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from scrapy.utils.python import unicode_to_str

def u_to_str(text):
    unicode_to_str(text,'latin-1','ignore')

class GenericItem(Item):

    # text items to be scraped
    title = Field(output_processor=u_to_str)        # title given by the owner
    text = Field(output_processor=u_to_str)         # description of the apt
    sub_area = Field(output_processor=u_to_str)     # area of apt
    adress = Field(output_processor=u_to_str)       # adress
    city = Field(output_processor=u_to_str)
    agence = Field(output_processor=u_to_str)

    # other
    area = Field()                  # location of the apt
    price = Field()                 # price asked for the apt
    coord = Field()                 # mappy geo coord
    furn = Field()                  # furnitures
    ref_n = Field()                 # reference number
    date = Field()                  # date of the reference
    surface = Field()               # surface of the apt
    rooms = Field()                 # number of rooms
    bedrooms = Field()              # number of bedrooms
    url = Field()                   # apt url (for debugging)
    construction_year = Field()
    charges = Field()
    floor = Field()
    balcon = Field()
    terasse = Field()
    agence = Field()
    charges = Field()
    heat = Field()                  # 0: individual
                                    # 1: collective
