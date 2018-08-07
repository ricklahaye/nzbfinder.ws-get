#!/usr/bin/python
import os
import sys
import urllib.request
import certifi
import json
import webbrowser


def sizeof_fmt(num, suffix='B'):    # convert size to human
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def get_api():
    try:
        f = open(os.path.expanduser("~/.config/nzbfinder_api.key"),"r")
    except:
        print("Error: file that holds API key not found")
        exit()

    try:
        api = f.readline()
        api = api.strip("\n")
        return api
    except:
        print("Error: reading API key in file failed")
        exit()

def get_search_parameter():
    try:
        if sys.argv[1] != "":
            search_parameter = sys.argv[1:]
            search_parameter = " ".join(search_parameter)            # combine arguments
            search_parameter = search_parameter.replace(" ", "+")   # replace space with + for url get with browser
            return search_parameter
    except:
        print("Error: given argument error")
        exit()


def get_data(api, search_parameter):
    try:
        r = urllib.request.urlopen('https://nzbfinder.ws/api?apikey=' + api + '&t=search&q=' + search_parameter + '&o=json')
        data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
        return data
    except:
        print("Error: failed getting hits from nzbfinder.ws, most likely wrong API key")
        exit()

def get_total_hits(data):
    try:
        total_hits = int(data['newznab:response']['_total'])
        print("Hits: " + str(total_hits))
        if total_hits == 0:
            print("No hits found, exitting")
            exit()
        return total_hits
    except:
        if total_hits != 0:        # only show error if error other than no hits
            print("Error: parsed data structure not expected, most likely API changed")
        exit()


def show_data(total_hits, data):
    lines_10_show = int(total_hits / 10)        # times 10 hits need to be shown
    lines_left_show = int(total_hits % 10)        # times the remaining hits need to be shown

    hits_shown = 0                                # counter for shown hits
    show_next = True                            # show next 10?

    while show_next:
        if lines_10_show == 0:                                        # if all 10 are shown, show remaining
            for i in range(lines_left_show):                            # show remaining
                hit_num = int(i + hits_shown + 1)
                hit_title = data['item'][hit_num - 1]['title']
                hit_size = int(data['item'][hit_num - 1]['newznab:attr'][1]['_value'])
                hit_date = data['item'][hit_num - 1]['pubDate']
                print(str(hit_num) + "\t" + hit_title + "\t" + sizeof_fmt(hit_size) + "\t" + hit_date + "\n")
            hits_shown += lines_left_show                                # add hits to counter
        else:                                                        # if not all 10 are shown, show 10
            for i in range(10):
                hit_num = int(i + hits_shown + 1)
                hit_title = data['item'][hit_num - 1]['title']
                hit_size = int(data['item'][hit_num - 1]['newznab:attr'][1]['_value'])
                hit_date = data['item'][hit_num - 1]['pubDate']
                print(str(hit_num) + "\t" + hit_title + "\t" + sizeof_fmt(hit_size) + "\t" + hit_date + "\n")
            hits_shown += 10                                            # add hits to counter
            lines_10_show -= 1                                            # remove 1 time from amount of time 10 need to be shown
        show_next = False                                            # do not show 10 new oness unless following conditions are met
        download_num = input("Download: ")

        if hits_shown == total_hits and download_num == "":            # if all hits are shown, and no input given
            while download_num == "":                                    # keep asking for input
                download_num = input("Download: ")
        elif download_num != "":                                    # if input given, break and download input
            break
        else:                                                        # else not all hits shown, or no input given
            show_next = True
    return data, download_num

def download_nzb(data, download_num):
    url = data['item'][int(download_num) - 1]['link']
    webbrowser.open(url, new=0, autoraise=True)

def main():
    api = get_api()                                     # get api key stored
    search_parameter = get_search_parameter()           # get search parameter
    data = get_data(api, search_parameter)              # get data from api
    total_hits = get_total_hits(data)                   # get total hits from data
    data, download_num = show_data(total_hits, data)    # show data and ask input
    download_nzb(data, download_num)                    # download nzb depending user input

try:
    while True:
        main()
except KeyboardInterrupt:
    exit()
