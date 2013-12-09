#!/usr/bin/python

from __future__ import print_function
from bs4 import BeautifulSoup, Comment
from time import gmtime, strftime
from urlparse import urljoin, urlparse
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


def create_dir():
    '''Create and return a unique directory to hold the downloaded data.'''
    dirname = "webdevdata.org-" + strftime("%Y-%m-%d-%H%M%S", gmtime())
    os.mkdir(dirname)
    return dirname


def connect(url, as_is=False):
    session = requests.Session()
    session.headers = REQUEST_HEADERS
    session.timeout = 3
    try:  # Request will follow redirects to https://, www., m., etc.
        if as_is:
            return session.get(url)
        else:
            return session.get("http://" + url)
    except requests.exceptions.RequestException as e:
        print("Exception in connect: ", e, url)


def get_hashdir(url):
    hash = hashlib.md5()
    hash.update(url)
    hash_dir = hash.hexdigest()[:2]
    if not os.path.exists(hash_dir):
        os.mkdir(hash_dir)
    return hash_dir


def inline_js(url, soup):
    for s in soup.find_all("script", src=True):
        base_elm = soup.find("base", href=True)
        if base_elm:
            base = base_elm['href']
        else:
            base = url
        # Protocol-relative URL, e.g., //foo.com/bar.js
        if s['src'].startswith("//"):
            script = connect(s['src'][2:])
        # Absolute URI, e.g., http://foo.com/bar.js
        elif urlparse(s['src'])[0] in ('http', 'https'):
            script = connect(s['src'], as_is=True)
        # All other relative URIs (../foo.js, js/foo.js)
        else:
            script = connect(urljoin("http://" + base, s['src']))
        tag = soup.new_tag("xscript")
        comment = soup.new_string("inlined by fetcher", Comment)
        tag.append(script.text)
        s.insert_before(comment)
        s.replace_with(tag)


def download_file(url, dir):
    os.chdir(dir)
    url = url.strip()
    try:
        print("Downloading: ", url)
        response = connect(url)
        dir = get_hashdir(url)
        ext = magic.from_buffer(response.content).split()[0].lower()
        filename = dir + "/" + url + "." + ext + ".txt"
        with open(filename, "wb") as local_file:
            local_file.write("Response status: " +
                             str(response.status_code) + "\n")
            for k, v in response.headers.iteritems():
                local_file.write("{}: {}\n".format(k, v))
            soup = BeautifulSoup(response.text)
            inline_js(url, soup)
            local_file.write("\n" + str(soup))
            local_file.close()
    except Exception as e:
        print("Exception:", e, url)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: {} create|download <URL> <dir>".format(sys.argv[0]))
    command = sys.argv[1]
    if command == "create":
        print(create_dir())
    elif command == "download":
        if len(sys.argv) < 4:
            sys.exit("Where's the URL and the directory?")
        download_file(sys.argv[2], sys.argv[3])
    else:
        sys.exit("Didn't understand the command")
