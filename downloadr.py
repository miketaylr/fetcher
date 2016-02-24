#!/usr/bin/python

import hashlib
import os
import sys
from time import gmtime, strftime
from urlparse import urljoin

# I don't even.
sys.path.insert(0, ('/Users/miket/dev/compat/fetcher/env/'
                    'lib/python2.7/site-packages'))

from bs4 import BeautifulSoup, Comment
import jsbeautifier
import requests

REQUEST_HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Linux; Android 6.0.1; Nexus 6P Build/MMB29Q) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/48.0.2564.95 Mobile Safari/537.36'),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',  # nopep8
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive'
}


def create_dir():
    '''Create and return a unique directory to hold the downloaded data.'''
    dirname = "fetcher-data-" + strftime("%Y-%m-%d", gmtime())
    os.mkdir(dirname)
    return dirname


def connect(url):
    session = requests.Session()
    session.headers = REQUEST_HEADERS
    session.max_redirects = 5
    session.timeout = 3
    if not url.startswith('http'):
        url = "http://" + url
    try:  # Request will follow redirects to https://, www., m., etc.
        res = session.get(url)
        if str(res.status_code).startswith(('4', '5')):
            return 'Non 2XX or 3XX response'
        return res.text
    except Exception as e:
        print("Problem fetching {0}!".format(url), e)
        return 'Failed due to an exception, (timeout, ssl, redirects) oops.'


def get_hashdir(url):
    hash = hashlib.md5()
    hash.update(url)
    hash_dir = hash.hexdigest()[:2]
    if not os.path.exists(hash_dir):
        os.mkdir(hash_dir)
    return hash_dir


def inline_js(url, soup):
    # jsbeautifier options
    # defaults at https://github.com/beautify-web/js-beautify#options
    opts = jsbeautifier.default_options()
    opts.indent_size = 2
    opts.preserve_newlines = False
    script_uri = ''

    # beautify all the inline scripts
    for s in soup.find_all("script", src=False):
        if s.string:
            s.string = "\n" + jsbeautifier.beautify(s.string, opts)

    # inline and beautify external scripts
    for s in soup.find_all("script", src=True):
        script = ''
        try:
            base_elm = soup.find("base", href=True)
            if base_elm:
                base = base_elm['href']
            else:
                # this assumes a http -> https redirect is in place.
                base = "http://" + url
            # Protocol-relative URL, e.g., //foo.com/bar.js
            if s['src'] and s['src'].startswith("//"):
                script_uri = s['src'][2:]
                script = connect(script_uri)
            # Absolute URI, e.g., http(s)://foo.com/bar.js
            elif s['src'].lower().startswith('http'):
                script_uri = s['src']
                script = connect(script_uri)
            # All other relative URIs (../foo.js, js/foo.js)
            elif s['src'][0] == '/' and s['src'][1] != '/':
                script_uri = urljoin(base, s['src'])
                script = connect(script_uri)
            tag = soup.new_tag("script")
            tag.append("\n" + jsbeautifier.beautify("// inlined: {0}\n".format(
                script_uri) + script, opts))
            s.insert_before("\n")
            s.replace_with(tag)
        except Exception as e:
            print("XXXxxxxEBugss xception!!!1: ", e)

            # TODO: async IO?
            # https://github.com/kennethreitz/grequest


def download_file(url, dir):
    os.chdir(dir)
    url = url.strip()
    try:
        response = connect(url)
        dir = get_hashdir(url)
        filename = dir + "/" + url + ".html"
        print("Fetching {0}".format(filename))
        with open(filename, "wb") as local_file:
            soup = BeautifulSoup(response, "lxml")
            inline_js(url, soup)
            local_file.write(str(soup))
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
