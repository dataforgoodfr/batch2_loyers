from crawlers_beta import PapCrawler, SeLogerCrawler

def run_tests():
    pap_test()
    # seloger_test()

def pap_test():
    
    url = 'http://www.pap.fr/annonces/appartement-paris-17e-r414100572'
    crawler = PapCrawler(url)
    data = crawler.__dict__

    for key, attr in data.items():
        print (key, ' : ', attr)

def seloger_test():
    
    url = (
        'http://www.seloger.com/annonces/locations/appartement/paris-6eme-75/odeon/114076879.htm'
    )

    crawler = SeLogerCrawler(url)
    data = crawler.__dict__
    print (data)

    print ('scraping_time : ', data['scraping_time'])
    print ('status : ', data['status'] )

if __name__ == '__main__':
    run_tests()

