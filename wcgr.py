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

aparser = argparse.ArgumentParser()
aparser.add_argument("-t", "--title-element", help="the identifier of the comic's issue title")
aparser.add_argument("url", help="the URL of the first comic page to grab")
args = aparser.parse_args()

print "URL: ", args.url
soup = BeautifulSoup(urllib.urlopen(args.url))

## process -t/--title-element flag
title=''
if args.title_element != None: # if we actually got the flag
#print soup.select("#ctitle")[0].string
    parts = args.title_element.split('/') # split it along slashes (only the first two parts will be used
    if len(parts) > 0: # if splitting went right (this should always hold, but yaknow, be safe)
        title_css_path = parts[0] # the first part is the actual CSS selector/path
        if title_css_path != None and len(title_css_path) > 0: #if the css path is not empty
            title_attribute = ''
            if len(parts) > 1: # if we actually have a second part
                title_attribute = parts[1] # then that second part is the attribute
            title_element = soup.select(title_css_path) # get the specified element(s)
            if len(title_element) > 0: # if we got some
                title_element = title_element[0] # pick only the first one
                if title_attribute == None or len(title_attribute) == 0: # empty attribute = use tag content
                    title = title_element.string
                else: # an attribute was really specified
                    title = title_element[title_attribute]
print "Title: ", title

