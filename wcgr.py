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

import os, sys, argparse
import urllib, urlparse
from bs4 import BeautifulSoup

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

def makeOutputFileName(url, outdir):
    global args
    result = outdir
    if args.number_width > 0:
        result += ('%0{}d_').format(args.number_width) % args.start_number
        args.start_number += 1
    result += os.path.basename(urlparse.urlparse(url).path)
    return result

def grabPage(url, title_element, image_element, next_element):
    global args, outdir
    try:
        soup = BeautifulSoup(urllib.urlopen(url))
    except IOError as e:
        e.strerror = "Error while trying to open URL \"{}\":\n\t{}".format(url, e.strerror)
        raise e

    title = getStrFromElement(soup, args.title_element)
    imgurl = getStrFromElement(soup, args.image_element)
    if args.verbose > 1:
        print "Raw image url: ", imgurl
    imgurl = urlparse.urljoin(url, imgurl)
    imgfile = makeOutputFileName(imgurl, outdir)
    nexturl = getStrFromElement(soup, args.next_element)

    if not args.quiet:
        print "Image URL: ", imgurl
        if args.verbose > 0:
            print 'Image file: ', imgfile
            print "Title: ", title
            print "Next URL: ", nexturl

    if not args.dry_run:
        urllib.urlretrieve(imgurl, imgfile)

    if args.verbose > 0:
        print "-----------------------------------------------------------------"
    
    return urlparse.urljoin(url, nexturl)
    

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
aparser.add_argument('-d', '--dry-run',
    action='store_true',
    help='only grab and display the URLs, do not actually download the files')
aparser.add_argument('-s', '--start-number',
    type=int,
    metavar='N',
    default=1,
    help='where to start when numbering the output files, default is 1')
aparser.add_argument('-w', '--number-width',
    type=int,
    metavar='N',
    default=4,
    help='how many digits to use for the running number in the output file '\
        'name, default is 4; use 0 to disable numbering of output files')
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
if not args.quiet:
    print ''
    # if verbose, dump the parsed arguments:
    if args.verbose > 1:
        print "Parsed arguments:\n", args
    # print how many pages we'll grab at most
    if args.count > 0:
        print "Grabbing at most {} pages, starting at:".format(args.count)
    else:
        print "Grabbing all available pages, starting at:"
    print "\t", args.url
    # get the output dir
    if args.output == None:
        outdir = './'
    else:
        outdir = args.output
    if not outdir.endswith(os.sep): # if the path does not end with a separator (denoting a folder)
        outdir += os.sep # append it
    if args.verbose > 0:
        print 'Saving output files to ', outdir
    
grabbedcount = 0 # counter for how many pages we've successfully grabbed
url = args.url

print ''
try:
    while url != None and len(url) > 0 and (args.count <= 0 or grabbedcount < args.count):
        newurl = grabPage(url, args.title_element, args.image_element, args.next_element)
        if newurl == url: # end-of-comic detection; TODO: make a list of visited pages?
            url = None
        else:
            url = newurl
        grabbedcount += 1
except IOError as e:
    print e.strerror
    sys.exit(1)
