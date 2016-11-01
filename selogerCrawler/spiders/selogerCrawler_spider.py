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





"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
					DEFINING ITEMS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

class SelogercrawlerItem(Item):

    titre=Field()
    ville=Field()
    piece=Field()
    chambre=Field()
    lien=Field()
    superficie=Field()
    agenceImmo=Field()
    prix=Field()
    charges=Field()
    typeOffre=Field()
    annonceId=Field()
    description=Field()
    detail=Field()
    etage=Field()
    balcon=Field()
    terasse=Field()
    balcon=Field()

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

            item['charges']=Selector(response).xpath('//*[@id="%s"]/div/div[2]/div/a/sup/text()'%annonce).extract()[0]
            i=i+1
            request=http.Request(url=item['lien'],dont_filter=True,callback=self.parse3)
            request.meta['item'] = item

            yield request

    def parse3(self,response):
        
        item = response.meta['item']
        description=Selector(response).xpath('//*[@id="detail"]/p[2]/text()').extract()
        item['description']=unidecode(description[0]) if description else ""
        details=Selector(response).xpath('//*[@id="detail"]/ol/li/text()').extract()
        item['detail']=list(map(lambda x:unidecode(' '.join(x.replace("\r\n",'').split())),details))
        
        return item