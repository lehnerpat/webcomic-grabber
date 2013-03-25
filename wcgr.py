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

import urllib, urlparse
from bs4 import BeautifulSoup

url = "https://xkcd.com/1/"

#soup = BeautifulSoup(urllib.urlopen(url))

#print "URL: ", url
#print "Title: ", soup.title.string

#img = soup.find(id="comic").img
#print "Image URL: ", img['src']
#print "Image subtext: ", img['title']

#print "Next: ", urlparse.urljoin(url, soup.find(id="middleContainer").ul.find(rel="next")['href'])
#print "Prev: ", urlparse.urljoin(url, soup.find(id="middleContainer").ul.find(rel="prev")['href'])

def getImageFrom(url):
    soup = BeautifulSoup(urllib.urlopen(url))
    
    print url, " | ", soup.title.string, " | ", soup.find(id="comic").img['src']
    
    return urlparse.urljoin(url, soup.find(id="middleContainer").ul.find(rel="next")['href'])

for i in range(10):
    url = getImageFrom(url)
