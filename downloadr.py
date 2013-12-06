#!/usr/bin/python

from __future__ import print_function
import hashlib
import magic
import os
import requests
import sys
from time import gmtime, strftime
# from urllib2 import HTTPError, URLError, urlopen

REQUEST_HEADERS = {'User-Agent': ('Mozilla/5.0 (Android; Mobile; rv:25.0) ')
                                  'Gecko/25.0 Firefox/25.0'),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate'
    'Connection': 'keep-alive'
}


def createDir():
    dirname = "webdevdata.org-" + strftime("%Y-%m-%d-%H%M%S", gmtime())
    os.mkdir(dirname)
    return dirname


def connect(url):
    session = requests.Session()
    session.max_redirects = 5
    session.get(url,
    try:
        f = urlopen("http://" + url)
        return f
    except URLError, e:
        try:
            f = urlopen("https://" + url)
            return f
        except URLError, e:
            try:
                f = urlopen("http://www." + url)
                return f
            except URLError, e:
                try:
                    f = urlopen("https://www." + url)
                    return f
                except HTTPError, e:
                    print("HTTPError:", e.code, url)
                except URLError, e:
                    print("URLError:", e.reason, url)


def downloadFile(url, dir):
    os.chdir(dir)
    url = url.strip()
    try:
        print("Downloading: ", url)
        if url.startswith("http://"):
            url = url[7:]
        if url.startswith("https://"):
            url = url[8:]
        urlhost = url.split("/")[0]
        urlpath = "/".join(url.split("/")[1:])
        f = connect(urlhost)
        hash = hashlib.md5()
        hash.update(url)
        dir = hash.hexdigest()[:2]
        if not os.path.exists(dir):
            os.mkdir(dir)
        buffer = f.read()
        ext = magic.from_buffer(buffer).split()[0].lower()
        if "html" in ext:
            ext = "html.txt"
        filename = dir + "/" + urlhost + "_" + hash.hexdigest() + "." + ext
        with open(filename, "wb") as local_file:
            local_file.write(buffer)
            local_file.close()
        with open(filename + ".hdr.txt", "wb") as local_file:
            local_file.write(str(f.getcode()) + "\n" + str(f.info()))
            local_file.close()
    except HTTPError, e:
        print("HTTPError:", e.code, url)
    except URLError, e:
        print("URLError:", e.reason, url)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:", sys.argv[0], "create|download <URL> <dir>",
              file=sys.stderr)
        quit()
    command = sys.argv[1]
    if command == "create":
        print(createDir())
    elif command == "download":
        if len(sys.argv) < 4:
            print("Where's the URL and the directory?", file=sys.stderr)
            quit()
        downloadFile(sys.argv[2], sys.argv[3])
    else:
        print("Didn't understand the command", file=sys.stderr)
