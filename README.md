GeoIP-Scraper
=============

Turn your log files containing IP addresses into a pretty little represantation of traffic inflow like this:

![](http://i.imgur.com/yf4NiPq.png)


How To Use
=========

First off, run ``pip install -r requirements.txt`` to install the external dependencies required.

Then simply run ``python geoip.py path/to/logfile.log``, this should generate a file under the web folder called data.json.
Simply place the web folder in a web-accessible area and open up geoip.html You should be met with the pretty generated map



The script also accepts input directly piped in to it, so for example if you rotate your logs you can simply do
``cat *log* | python geoip.py``
or feed in multiple files like so
``python geoip.py 1.log 2.log``
