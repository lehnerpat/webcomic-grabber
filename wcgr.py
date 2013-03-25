#!/usr/bin/env python
########
# Copyright (C) 2013 Nevik Rehnel <hai.kataker@gmx.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
########

import sys, argparse
import urllib, urlparse
from bs4 import BeautifulSoup

#url = "https://xkcd.com/1/"

##First testing code: (xkcd)
#soup = BeautifulSoup(urllib.urlopen(url))

#print "URL: ", url
#print "Title: ", soup.title.string

#img = soup.find(id="comic").img
#print "Image URL: ", img['src']
#print "Image subtext: ", img['title']

#print "Next: ", urlparse.urljoin(url, soup.find(id="middleContainer").ul.find(rel="next")['href'])
#print "Prev: ", urlparse.urljoin(url, soup.find(id="middleContainer").ul.find(rel="prev")['href'])

##Second testing code: (xkcd)
#def getImageFrom(url):
#    soup = BeautifulSoup(urllib.urlopen(url))
#    
#    print url, " | ", soup.title.string, " | ", soup.find(id="comic").img['src']
#    
#    return urlparse.urljoin(url, soup.find(id="middleContainer").ul.find(rel="next")['href'])
#
#for i in range(10):
#    url = getImageFrom(url)

def getStrFromElement(soup, specifier):
    result=''
    if specifier != None: # if we actually got a specifier
        parts = specifier.rsplit('/', 1) # split it along slashes (only the first two parts will be used)
        if len(parts) > 0: # if splitting went right (this should always hold, but yaknow, be safe)
            css_path = parts[0] # the first part is the actual CSS selector/path
            if css_path != None and len(css_path) > 0: # if the css path is not empty
                attr_name = ''
                if len(parts) > 1: # if we actually have a second part
                    attr_name = parts[1] # then that second part is the attribute name
                element = soup.select(css_path) # get the specified element(s)
                if len(element) > 0: # if we got some
                    element = element[0] # pick only the first one
                    if attr_name == None or len(attr_name) == 0: # empty attribute = use tag content
                        result = element.string
                    else: # an attribute was really specified
                        result = element[attr_name]
    return result

def grabPage(url, title_element, image_element, next_element):
    global args
    try:
        soup = BeautifulSoup(urllib.urlopen(url))
    except IOError as e:
        e.strerror = "Error while trying to open URL \"{}\":\n\t{}".format(args.url, e.strerror)
        raise e

    title = getStrFromElement(soup, args.title_element)
    imgurl = getStrFromElement(soup, args.image_element)
    nextel = getStrFromElement(soup, args.next_element)

    print "Title: ", title
    print "Image URL: ", imgurl
    print "Next URL: ", nextel
    

## Prepare and parse the command line arguments 
helpepilog = """
To select/extract a string from somewhere in the HTML document, you can use a
STR_SPEC of the following format:
\t<CSS Selector>[/<attribute name>]
That is, a CSS selector to specify the HTML tag, optionally followed by a slash
and an attribute name. If more than one tag match the CSS selector, the first
one will be selected. If an attribute name is given, the value of that 
attribute will be used as result; if no attribute name is given (the slash can
be left out in that case, too), the selected tag's text content will be used
instead.
"""
aparser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=helpepilog
)
group = aparser.add_mutually_exclusive_group()
group.add_argument("-q", "--quiet",
    action="store_true",
    help="make the script perform silently, suppressing normal output; note\
        that Python errors will still be printed")
group.add_argument("-v", "--verbose",
    action="count",
    help="make the script more verbose, explaining what it does as it goes\
        along")
del group
aparser.add_argument("-t", "--title-element",
    metavar="STR_SPEC",
    help="the specifier of the comic's issue title")
aparser.add_argument("-i", "--image-element",
    metavar="STR_SPEC",
    help="the specifier of the comic's image URL")
aparser.add_argument("-n", "--next-element",
    metavar="STR_SPEC",
    help="the specifier of the link to the next issue page")
aparser.add_argument("-o", "--output",
    metavar="DIR",
    help="output directory for downloaded files; must be writable; defaults\
        to current directory")
aparser.add_argument("-c", "--count",
    type=int,
    metavar="N",
    help="maximum number of pages to grab")
aparser.add_argument("url", help="the URL of the first comic page to grab")
args = aparser.parse_args()


## additional sanity checking on arguments
if args.title_element == None or len(args.title_element) == 0 \
        or args.image_element == None or len(args.image_element) == 0:
    if not args.quiet:
        print "Error: No 'title' element or no 'image' element was specified.\n"\
            "Cannot grab comic. Aborting."
    sys.exit(1)

if args.next_element == None or len(args.next_element) == 0:
    if not args.quiet:
        print "Warning: No 'next' element was specified, can only grab the "\
            "given URL,\nno following pages\n"
    args.count = 1


## print some info about what we're gonna do
if args.verbose > 1:
    print "Parsed arguments:\n", args
if not args.quiet:
    if args.count > 0:
        print "Grabbing at most {} pages, starting at:".format(args.count)
    else:
        print "Grabbing all available pages, starting at:"
    print "\t", args.url
grabbedcount = 0 # counter for how many pages we've successfully grabbed
url = args.url

try:
    grabPage(url, args.title_element, args.image_element, args.next_element)
except IOError as e:
    print e.strerror
    sys.exit(1)
