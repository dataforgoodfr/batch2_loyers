from crawlers import PapCrawler, SeLogerCrawler

def run_tests():
    # pap_test()
    seloger_test()

def pap_test():
    
    url = 'http://www.pap.fr/annonce/locations-paris-75-g439-r413900125?u=1'
    crawler = PapCrawler(url)
    crawler.run()

    assert type(crawler.item['rent_cc']) == float
    assert type(crawler.item['desc']) == str
    assert type(crawler.item['url']) == str
    assert type(crawler.item['area']) == str
    assert type(crawler.item['surface']) == float
    assert type(crawler.item['coord']) == list
    assert type(crawler.item['address']) == str
    assert type(crawler.item['furnitures']) == bool

    for key, attr in crawler.item.items():
        print (key, ':', attr)

    print ('scraping_time : ', crawler.scraping_time)
    print ('status : ', crawler.status )

def seloger_test():
    
    url = (
        'http://www.seloger.com/annonces/locations/appartement/paris-5eme-75/val-de-grace/114459369.htm?cp=75&idtt=1&idtypebien=1&tri=initial'
    )

    crawler = SeLogerCrawler(url)
    crawler.run()

    print (crawler.item['area'])
    assert type(crawler.item['rent_cc']) == float
    assert type(crawler.item['desc']) == str
    assert type(crawler.item['url']) == str
    assert type(crawler.item['area']) == str
    assert type(crawler.item['surface']) == float
    assert type(crawler.item['coord']) == list
    assert type(crawler.item['address']) == str

    for key, attr in crawler.item.items():
        print (key, ':', attr)

    print ('scraping_time : ', crawler.scraping_time)
    print ('status : ', crawler.status )

if __name__ == '__main__':
    run_tests()