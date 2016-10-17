// Author: Samuel DELCOURT, for Data For Good

var casper = require('casper').create({
    verbose: true,
    //logLevel: 'debug', // To remove when works !
    pageSettings: {
         userAgent: 'Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.1)',
		 loadImages:  false,        // do not load images
         loadPlugins: false         // do not load NPAPI plugins (Flash, Silverlight, ...)
    }
});


var arguments = casper.cli.args;
if(arguments.length!=1){
  casper.echo('ERROR ! Need 1 argument : url_page_to_scrape', 'ERROR');
  casper.exit();
}
var url_to_scrape = arguments[0];

function print_page_content(){
  var page = casper.evaluate(function() {
    return document.documentElement.innerHTML;
  });
  casper.echo(page);
}

casper.start(url_to_scrape, function() {
  if(this.status().currentHTTPStatus != 200){
    this.echo('Connexion failed', 'ERROR');
    // Stop the script
    //capser.done();
	this.echo('!&!Connexion failed!&!');
  } else {

	casper.then(function(){
      if(this.exists('div[class="detailedSheetContainer"] div[class="notOnTheMarketLabel"] span')) {
        casper.echo('!&!Not anymore to sell!&!');
      } else {
        casper.waitForSelector('div[class="contact-name"]', function() {
          },function(){},30000);
        

        casper.then(function(){
          print_page_content();
        });
      }
    });

  }
});


casper.run();
