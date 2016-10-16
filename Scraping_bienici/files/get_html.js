// Author: Samuel DELCOURT, for Data For Good

var casper = require('casper').create({
    verbose: true,
    //logLevel: 'debug', // To remove when works !
    pageSettings: {
         userAgent: 'Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.1)'
    }
});

var arguments = casper.cli.args;
if(arguments.length!=1){
  casper.echo('ERROR ! Need 1 argument : url_page_to_scrape', 'ERROR');
  abc; //This lines means nothing, and then stop the script
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
    capser.exit();
  }
});

casper.then(function(){
  casper.waitForSelector('div[class="resultsListContainer"] article', function() {
  },function(){},60000);
});

casper.then(function(){
  print_page_content();
});
casper.run();
