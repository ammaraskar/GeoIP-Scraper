import os, sys, threading, re
import json
import urllib2
import gzip
import pygeoip

progress_bar_space = 35
url = "http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz"


class DownloadThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)

    def run(self):
        file_name = url.split('/')[-1]
        u = urllib2.urlopen(url)
        f = open(file_name, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print("Downloading: %s Bytes: %s" % (file_name, file_size))

        file_size_dl = 0
        block_sz = 8192
        last_perc = -10
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break
            file_size_dl += len(buffer)
            f.write(buffer)

            percentage = (file_size_dl * 100. / file_size)
            if (percentage - last_perc) > .9:

                characters = int(percentage / 100 * progress_bar_space)
                deficit = progress_bar_space - characters

                status = "%.1f%% [%s%s]" % (percentage, "=" * characters, " " * deficit)

                last_perc = percentage
                print status

        print("GeoIP file downloaded, extracting.")
        f.close()
        f = gzip.open(file_name, 'rb')
        with open('GeoIPCity.dat', 'wb') as out:
            out.write(f.read())
        f.close()


def scrape_file(IPFile, IPs):
    with open(IPFile) as IPFile:
        for line in IPFile:
            extract_ip(line, IPs)


# If there is an ip in this line, it'll be added to the collection
def extract_ip(line, IPs):
    match = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line)
    if len(match) > 0:
        IPs |= set(match)


def detect_string(string, IPs):
    if os.path.exists(string):
        scrape_file(string, IPs)
    else:
        extract_ip(string, IPs)


def main():
    IPs = set()

    downloadThread = None
    if not os.path.exists("GeoIPCity.dat"):
        downloadThread = DownloadThread()
        downloadThread.start()

    if not sys.stdin.isatty():
        for line in sys.stdin:
            detect_string(line, IPs)

    for arg in sys.argv[1:]:
        detect_string(arg, IPs)
        
    if downloadThread:
        downloadThread.join()

    print("Detected " + str(len(IPs)) + " IP address(es)")

    gi = pygeoip.GeoIP('GeoIPCity.dat', pygeoip.const.MEMORY_CACHE)
    data = []

    last_perc = -5
    total = len(IPs)
    done = 0
    for ip in IPs:
        try:
            info = gi.record_by_addr(ip)
            data.append({'lat' : info['latitude'],
                         'long' : info['longitude']})
        except:
            pass
        done += 1
        percentage = done * 100. / total
        if percentage - last_perc > 5:
            print(("%.1f" % percentage) + "% IPs processed")
            last_perc = percentage

    with open('web/data.json', 'w+') as dataFile:
        dataFile.write("var data = ")
        json.dump(data, dataFile)

if __name__ == "__main__":
    main()