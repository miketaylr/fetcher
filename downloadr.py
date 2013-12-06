#!/usr/bin/python

from __future__ import print_function
from time import gmtime, strftime
import hashlib
import magic
import os
import requests
import sys

REQUEST_HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Android; Mobile; rv:25.0) '
                   'Gecko/25.0 Firefox/25.0'),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive'
}


def createDir():
    dirname = "webdevdata.org-" + strftime("%Y-%m-%d-%H%M%S", gmtime())
    os.mkdir(dirname)
    return dirname


def connect(url):
    session = requests.Session()
    session.headers = REQUEST_HEADERS
    session.timeout = 3
    try:  # Request will follow redirects to https://, www., m., etc.
        return session.get("http://" + url)
    except requests.exceptions.RequestException as e:
        print("Exception: ", e, url)


def downloadFile(url, dir):
    os.chdir(dir)
    url = url.strip()
    try:
        print("Downloading: ", url)
        response = connect(url)
        hash = hashlib.md5()
        hash.update(url)
        dir = hash.hexdigest()[:2]
        if not os.path.exists(dir):
            os.mkdir(dir)
        ext = magic.from_buffer(response.content).split()[0].lower()
        if "html" in ext:
            ext = "html.txt"
        filename = dir + "/" + url + "_" + hash.hexdigest() + "." + ext
        with open(filename, "wb") as local_file:
            local_file.write(response.text.encode('utf8'))
            local_file.close()
        with open(filename.rstrip(".txt") + ".hdr.txt", "wb") as local_file:
            local_file.write(str(response.status_code) + "\n")
            for k, v in response.headers.iteritems():
                local_file.write("{}: {}\n".format(k, v))
            local_file.close()
    except Exception as e:
        print("Exception:", e, url)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: {} create|download <URL> <dir>".format(sys.argv[0]))
    command = sys.argv[1]
    if command == "create":
        print(createDir())
    elif command == "download":
        if len(sys.argv) < 4:
            sys.exit("Where's the URL and the directory?")
        downloadFile(sys.argv[2], sys.argv[3])
    else:
        sys.exit("Didn't understand the command")
