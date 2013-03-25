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

import argparse
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
        parts = specifier.split('/', 1) # split it along slashes (only the first two parts will be used)
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
    

aparser = argparse.ArgumentParser()
aparser.add_argument("-t", "--title-element", help="the identifier of the comic's issue title")
aparser.add_argument("url", help="the URL of the first comic page to grab")
args = aparser.parse_args()

print "URL: ", args.url
soup = BeautifulSoup(urllib.urlopen(args.url))

## process -t/--title-element flag
print "Title: ", getStrFromElement(soup, args.title_element)

