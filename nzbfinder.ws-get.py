import os
import sys
import urllib.request
import certifi
import json
import webbrowser


def sizeof_fmt(num, suffix='B'):                            # convert size to human
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def get_api():                                              # get api stored
    global api
    f = open(os.path.expanduser("~/.config/nzbfinder_api.key"),"r")
    api = f.readline()
    api = api.strip("\n")

def get_hits():
    global item

    search = sys.argv[1:]                                   # parse arg
    search = " ".join(search)                               # combine arguments
    search = search.replace(" ", "+")                       # replace space with + for url get with browser

    r = urllib.request.urlopen('https://nzbfinder.ws/api?apikey=' + api + '&t=search&q=' + search + '&o=json', cafile=certifi.where())
    data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))


    item = data['item']
    hits = data['newznab:response']['_total']
    print("Hits: " + hits)

    for i in range(10):
        hit = str(i + 1)
        title = item[i]['title']
        size = int(item[i]['newznab:attr'][1]['_value'])
        date = item[i]['pubDate']
        print(hit + "\t" + title + "\t" + sizeof_fmt(size) + "\t" + date + "\n")

def download_nzb():
    download_num = input("Download: ")
    url = item[int(download_num) - 1]['link']
    webbrowser.open(url, new=0, autoraise=True)

get_api()
get_hits()
download_nzb()
