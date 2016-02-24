# Fetcher

Scripts used to fetch the HTML files from top Alexa sites.

Note that this is Mike Taylor's fork, which swapped in Requests for urllib2, makes it a bit more Pythonic, and inlines external JS files. This is more useful for me to do research on DOM APIs used throughout the web.

#### TODO:

* Tests
* Beautify JS
* Make it fast (took like 8 hours to download ~62,000 pages)

## Methodology

* The top 1 million Alexa sites
[csv](http://s3.amazonaws.com/alexa-static/top-1m.csv.zip) is
downloaded, unzipped, and the URLs are extracted from it
* The URLs are then fed to a Python script that downloads the HTML files
and their HTTP headers using a thread pool (to minimize waiting).

## Usage

If your on Linux or OSX, simply run `./getData.sh` and you should be
good to go.
If you're on Windows, [cygwin](http://www.cygwin.com/) may be your best
bet.

If you want to fetch resources other than Alexa's top HTMLs, you can do
that by doing something like `cat urls.txt | xargs -I % -n 1 -P64 ./downloadr.py download % webdevdata.org-2013-12-06-200358/`

## Dependencies

* Python (Tested with 2.7)
* curl
* zcat
* [python-magic](https://github.com/ahupp/python-magic)
* lxml

Don't forget to install libmagic for Python magic to work:

https://github.com/ahupp/python-magic#dependencies

## Results

The resulting directory structure is:

* A root directory of the pattern "webdevdata.org-YYYY-MM-DD-HHMMSS"
* Sub-directories are 16 bit hashes of the URLs below them. Used to
verify there are not toom many files in a single directory.

The resulting files have an ".html.txt" extension for the data files and
".html.hdr.txt" extension for the header files.

## <a href="http://www.html5accessibility.com/HTMLdata/webdevdata.org-2013-10-30.7z">October 2013 data set (780 Mb, .7z file)</a>
Includes approx 78,000 HTML files.

## <a href="http://www.html5accessibility.com/HTMLdata/webdevdata.org-2013-06-18.7z">June 2013 data set (484 Mb, .7z file)</a>
Includes approx 53,000 HTML files.
Some HTML element and attribute <a href="https://docs.google.com/spreadsheet/ccc?key=0AlVP5_A996c5dFhMQ3R2SG1uZFNZVEsxUURQN213VVE#gid=0">usage stats</a> derived from the data are available.

## Queries
A java based script is available to get statistics on html tags/attributes with CSS-like queries.

See the [Queries on WebDevData](https://github.com/baptistelebail/webdevdata.org/wiki/Queries-on-WebDevData) wiki.
