# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 21:08:09 2016

@author: anouar
"""

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                                SELOGER.COM CRAWLER SPIDER
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

from scrapy import Item,Field,Spider,http
from scrapy.selector import Selector
from unidecode import unidecode
from math import ceil
from re import sub





"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
					DEFINING ITEMS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

class SelogercrawlerItem(Item):

    titre=Field()
    ville=Field()
    quartier=Field()
    piece=Field()
    chambre=Field()
    lien=Field()
    anneeConst=Field()
    superficie=Field()
    agenceImmo=Field()
    prix=Field()
    chargesType=Field()
    chargesMontant=Field()
    typeOffre=Field()
    annonceId=Field()
    description=Field()
    detail=Field()
    etage=Field()
    balcon=Field()
    terasse=Field()
    balcon=Field()
    Geo_NE_Lat=Field()
    Geo_NE_Long=Field()
    Geo_SW_Lat=Field()
    Geo_SW_Long=Field()
    Geo_Lat=Field()
    Geo_Long=Field()
    Geo_Type=Field()

    pass




"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
					DEFINING SPIDER
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


class seLogerCrawlerSpider(Spider):

    name = "selogerCrawler"
    allowed_domains = ["seLoger.com"]
    start_urls=[]

    def __init__(self,cp=None):
        urlCp="http://www.seloger.com/list.htm?idtt=1&idtypebien=2,1,9&cp=%s&tri=initial"
        self.start_urls=[urlCp%cp]
        self.logger.info("\n\n\n>>>START URL=%s"%self.start_urls)

    def parse(self,response):

        nbRes1=Selector(response).xpath('//*[@id="modalWrapper"]/div[2]/div[3]/div[3]/div[1]/div/text()').extract()
        nbRes2=Selector(response).xpath('//*[@id="modalWrapper"]/div[2]/div[4]/div[3]/div[1]/div/text()').extract()
        tmp=nbRes1+nbRes2
        self.logger.info("\n\n\n>>>NbAnnonces=%s"%tmp)
        
        if tmp:
            
            nbRes=int(tmp[0].split(' annonces')[0])
        else:
            item = SelogercrawlerItem()
            yield item

        nbResPages=int(ceil(nbRes/20))# 20 res/page
        url=response.url
        headers={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en',
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'}
        
        for i in range(1,nbResPages+1):
            yield http.Request(url=url+'&LISTING-LISTpg='+str(i),dont_filter=True,callback=self.parse2,headers=headers)

    def parse2(self, response):

        i=1
        self.logger.info("\n\n\n>>>AnnoncesPageURl=%s"%response.url)
        annonces1=Selector(response).xpath('//*[@id="modalWrapper"]/div[2]/div[3]/div[4]/div/div/section/article/@id').extract()
        annonces2=Selector(response).xpath('//*[@id="modalWrapper"]/div[2]/div[4]/div[4]/div/div/section/article/@id').extract()
        annonces=annonces1+annonces2

        for annonce in annonces:
            
            self.logger.info("\n>>>>Annonce Number=%s"%i)
            item = SelogercrawlerItem()

            item['annonceId']=annonce

            titre=Selector(response).xpath('//*[@id="%s"]/div/div[2]/h2/a/text()'%annonce).extract()
            item['titre'] =unidecode(titre[0])

            ville=Selector(response).xpath('//*[@id="%s"]/div/div[2]/h2/a/span/text()'%annonce).extract()
            item['ville'] =unidecode(ville[0])

            prix=Selector(response).xpath('//*[@id="%s"]/div/div[2]/div/a/text()'%annonce).extract()
            prix=unidecode(prix[0])
            try:
                item['prix']=float(prix.split(" EUR")[0].replace(' ',''))
            except:
                 self.logger.info('Couldnt parse price')

            mainDetails=Selector(response).xpath('//*[@id="%s"]/div/div[2]/ul/li/text()'%annonce).extract()
            self.logger.info('\n\n>>>>>Main Details: %s'%mainDetails)
            for detail in mainDetails:
                if ' p' in detail:
                    item['piece']=int(detail.split(' p')[0])
                elif ' chb' in detail:
                    item['chambre']=int(detail.split(' chb')[0])
                elif 'm2' in detail:
                    item['superficie']=float(detail.split(" m2")[0].replace(',','.'))
                elif 'etg' in detail:
                    item['etage']=int(detail.split(' etg')[0])
                elif ' tess' in detail:
                    item['terasse']=int(detail.split(' tess')[0])
                elif 'balc' in detail:
                    item['balcon']=int(detail.split(' balc')[0])

            try:
                item['lien']=Selector(response).xpath('//*[@id="%s"]/div/div[2]/h2/a/@href'%annonce).extract()[0]
            except:
                self.logger.info('Couldnt parse lien')

            agence1=Selector(response).xpath('//*[@id="%s"]/div/div[3]/div[1]/p/a/img/@alt'%annonce).extract()
            agence2=Selector(response).xpath('//*[@id="%s"]/div/div[3]/div[1]/p/img/@alt'%annonce).extract()
            agence3=Selector(response).xpath('//*[@id="%s"]/div/div[3]/p/span/text()'%annonce).extract()
            if len(agence3)!=0 and len(agence1)==0 and len(agence2)==0:

                item['agenceImmo']=unidecode(agence3[0])
                item['typeOffre']="Particulier"

            else:

                item['agenceImmo']=unidecode(agence1[0]) if len(agence2)==0 else unidecode(agence2[0])
                item['typeOffre']="Agence"

            item['chargesType']=Selector(response).xpath('//*[@id="%s"]/div/div[2]/div/a/sup/text()'%annonce).extract()[0]

            i=i+1
            request=http.Request(url=item['lien'],dont_filter=True,callback=self.parse3)
            request.meta['item'] = item

            yield request

    def parse3(self,response):
        
        item = response.meta['item']
        quartier=response.xpath('//div[1]/div[1]/h1/span/@title').extract()
        item['quartier']=unidecode(quartier[0].split("Quartier ")[-1]) if quartier else ""

        description=Selector(response).xpath('//*[@id="detail"]/p[2]/text()').extract()
        item['description']=unidecode(description[0]) if description else ""

        details=Selector(response).xpath('//*[@id="detail"]/ol/li/text()').extract()
        details=list(map(lambda x:unidecode(' '.join(x.replace("\r\n",'').split())),details))
        item['detail']=details
        temp=list(map(lambda x:chargesAnneeConstFinder(x,item),details))

        #Polygon Geoposition
        nePointLat=Selector(response).xpath('//*[@id="resume__map_new"]/@data-boudingbox-northeast-latitude').extract()
        if nePointLat:
            item['Geo_NE_Lat']=nePointLat[0]
        nePointLong=Selector(response).xpath('//*[@id="resume__map_new"]/@data-boudingbox-northeast-longitude').extract()
        
        if nePointLong:
            item['Geo_NE_Long']=nePointLong[0]
        
        swPointLat=Selector(response).xpath('//*[@id="resume__map_new"]/@data-boudingbox-southwest-latitude').extract()
        if swPointLat:
            item['Geo_SW_Lat']=swPointLat[0]
        
        swPointLong=Selector(response).xpath('//*[@id="resume__map_new"]/@data-boudingbox-southwest-longitude').extract()
        if swPointLong:
            item['Geo_SW_Long']=swPointLong[0]
        
        if nePointLat or nePointLong or swPointLat or swPointLong:
            item['Geo_Type']="rectangle"

        #Exact Geoposition
        exactPointLat=Selector(response).xpath('//*[@id="resume__map_new"]/@data-coordonnees-latitude').extract()
        exactPointLong=Selector(response).xpath('//*[@id="resume__map_new"]/@data-coordonnees-longitude').extract()
        if exactPointLat:
            item['Geo_Lat']=exactPointLat[0]
        
        if exactPointLong:
            item['Geo_Long']=exactPointLong[0]
        
        if exactPointLat or exactPointLong:
            item['Geo_Type']="point"
        
        return item

def chargesAnneeConstFinder(x,d):
    ch=x.lower()
    if "charges" in ch:
        temp=sub(r'[^\w. ]', '', ch)
        temp=temp.split("charges ")[-1]
        try:
            temp=float(temp.split(" eur")[0].replace(' ',''))
            d["chargesMontant"]=temp
        except:
            d["charges"]=""
    
    if "annee de construction" in ch:
        temp=sub(r'[^\w. ]', '', ch)
        temp=temp.split("annee de construction")[-1]
        try:
            d['anneeConst']=int(temp)
        except:
            d['anneeConst']=""