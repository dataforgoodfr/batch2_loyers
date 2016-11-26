from crawlers import PapCrawler, SeLogerCrawler

def run_tests():
    # pap_test()
    seloger_test()

def pap_test():
    
    url = 'http://www.pap.fr/annonce/locations-paris-75-g439-r413900125?u=1'
    crawler = PapCrawler(url)

    print ('scraping_time : ', crawler.scraping_time)
    print ('status : ', crawler.status )

def seloger_test():
    
    url = (
        'http://www.seloger.com/annonces/locations/appartement/paris-6eme-75/odeon/114076879.htm'
    )

    crawler = SeLogerCrawler(url)

    print ('scraping_time : ', crawler.scraping_time)
    print ('status : ', crawler.status )

if __name__ == '__main__':
    run_tests()

