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
import urllib2, urlparse
from lxml import etree, html
from lxml.cssselect import CSSSelector

try:
    import requests
    libRequestsAvail = True
except ImportError:
    libRequestsAvail = False

# @param alias_url the url for which to find a template
# @param aliases_file the list of alias-template mappings
# @returns the template ID (`int`) for the first matching alias, or
#       `None` if no match was found
def lookupTemplateFromAlias(alias_url, aliases_file):
    global args
    c = 0 # line counter
    templ_id = None
    f = open(aliases_file, 'r')
    for line in f:
        c += 1
        line = line.strip()
        # skip empty lines and comment lines
        if line == None or len(line) == 0 or line[0] == '#':
            continue
        parts = line.split('|')
        if parts == None or len(parts) < 2:
            if args.verbose > 0:
                print '  {}, line {}: malformed line, ignoring'.format(aliases_file, c)
            continue # ignore the malformed line
        alias = parts[0].strip()
        if alias.startswith('{') and alias.endswith('}'): # this is a regexp
            regex = alias[1:-1] # strip the containing curly braces
            if regex == None or len(regex) <= 0:
                if args.verbose > 0:
                    print '  {}, line {}: empty, ignoring'.format(aliases_file, c)
                continue # drop the empty regex
            # TODO: implement handling regexp
        else: # otherwise, this is a simple prefix
            if alias_url.startswith(alias):
                try:
                    templ_id = int(parts[1].strip())
                    break
                except ValueError:
                    if args.verbose > 0:
                        print '  {}, line {}: malformed template ID (must be int), ignoring'.format(aliases_file, c)
    f.close()
    return templ_id

# @returns a string containing argparse arguments or `None` if the given ID was not found
def getTemplate(template_id, templates_file):
    global args
    argresult = None # resulting string
    c = 0 # line counter
    f = open(templates_file)
    for line in f:
        c += 1
        line = line.strip()
        # skip empty lines and comment lines
        if line == None or len(line) == 0 or line[0] == '#':
            continue
        parts = line.split('|')
        if parts == None or len(parts) < 2:
            if args.verbose > 0:
                print '  {}, line {}: malformed line, ignoring'.format(templates_file, c)
            continue # ignore the malformed line
        try:
            line_id = int(parts[0].strip())
            if line_id == template_id: # if this line matches the requested ID
                argresult = parts[1].strip()
        except ValueError:
            if args.verbose > 0:
                print '  {}, line {}: malformed template ID (must be int), ignoring'.format(templates_file, c)
    f.close()
    return argresult

def getStrFromElement(tree, specifier):
    result=''
    if specifier != None: # if we actually got a specifier
        parts = specifier.rsplit('/', 1) # split it along slashes (only the first two parts will be used)
        if len(parts) > 0: # if splitting went right (this should always hold, but yaknow, be safe)
            css_path = parts[0] # the first part is the actual CSS selector/path
            if css_path != None and len(css_path) > 0: # if the css path is not empty
                attr_name = ''
                if len(parts) > 1: # if we actually have a second part
                    attr_name = parts[1] # then that second part is the attribute name
                sel = CSSSelector(css_path)
                element = sel(tree) # get the specified element(s)
                if len(element) > 0: # if we got some
                    element = element[0] # pick only the first one
                    if attr_name == None or len(attr_name) == 0: # empty attribute = use tag content
                        result = element.text
                    else: # an attribute was really specified
                        result = element.get(attr_name)
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
        if args.verbose > 2:
            print "Fetching HTML from ", url
        if libRequestsAvail:
            r = requests.get(url)
            src = r.content
        else:
            src = urllib2.urlopen(url).read()
        tree = etree.fromstring(src, parser=html.HTMLParser())
        if args.verbose > 2:
            print "\tResult: ", tree
    except IOError as e:
        e.strerror = "Error while trying to open URL \"{}\":\n\t{}".format(url, e.strerror)
        raise e

    title = getStrFromElement(tree, args.title_element)
    imgurl = getStrFromElement(tree, args.image_element)
    if args.verbose > 1:
        print "Raw image url: ", imgurl
    imgurl = urlparse.urljoin(url, imgurl)
    imgfile = makeOutputFileName(imgurl, outdir)
    nexturl = getStrFromElement(tree, args.next_element)

    if not args.quiet:
        print "Image URL: ", imgurl
        if args.verbose > 0:
            print 'Image file: ', imgfile
            print "Title: ", title
            if args.verbose > 1:
                print "Raw next URL: ", nexturl
    nexturl = urlparse.urljoin(url, nexturl)
    if args.verbose > 0:
        print "Next URL: ", nexturl

    if not args.dry_run: # if we're not in dry run mode, actually get the image
        if libRequestsAvail: # if requests is available
            r = requests.get(imgurl)
            with open(imgfile, "wb") as outfile:
                outfile.write(r.content)
        else: # otherwise, fall back to urllib2
            f = urllib2.urlopen(imgurl)
            with open(imgfile, "wb") as outfile:
                outfile.write(f.read())

    if args.verbose > 0:
        print "-----------------------------------------------------------------"
    
    return nexturl
    

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
group = aparser.add_mutually_exclusive_group()
group.add_argument('-a', '--auto',
    action='store_true',
    help='try to find a matching template from the URL')
group.add_argument('-e', '--template',
    type=int,
    metavar='ID',
    help='use the template with the given ID')
group.add_argument('--alias',
    dest='aliasurl',
    help='use the given ALIAS to select the template instead of the given URL')
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
aparser.add_argument('--templates-file',
    metavar='FILE',
    default='templates/wcgr_templates.txt',
    help='use this file to look up templates; default is "templates/wcgr_templates.txt"')
aparser.add_argument('--aliases-file',
    metavar='FILE',
    default='templates/wcgr_aliases.txt',
    help='use this file to look up URL aliases for templates; default is '\
        '"templates/wcgr_aliases.txt"')
aparser.add_argument("url", help="the URL of the first comic page to grab")
args = aparser.parse_args()

print ''

# if verbose, dump the parsed arguments:
if args.verbose > 1:
    print "Parsed arguments:\n", args, '\n'

## if requested, let's try to load the template
if args.auto: # we use the comic URL to look up the template
    args.aliasurl = args.url
if args.aliasurl != None: # we use that alias URL to look up the template
    try:
        if args.verbose > 1:
            print 'Looking up template for URL {} in {}'.format(args.aliasurl, args.aliases_file)
        args.template = lookupTemplateFromAlias(args.aliasurl, args.aliases_file)
        if not args.quiet and args.template == None:
            print ('Error: No matching template was found for URL {} in aliases '\
                'list {}').format(args.aliasurl, args.aliases_file)
        if args.verbose > 1 and args.template != None:
            print 'Template ID for {} is {}'.format(args.aliasurl, args.template)
    except IOError as e:
        if not args.quiet:
            print 'An error occurred while reading aliases from {}'.format(args.aliases_file)
        if args.verbose > 0:
            print '\t', e
        args.template = None
if args.template != None: # let's use the template that's specified or found
    try:
        if args.verbose > 1:
            print 'Looking for template {} in {}'.format(args.template, args.templates_file)
        templstr = getTemplate(args.template, args.templates_file)
        if not args.quiet and templstr == None:
            print 'Error: Template {} was not found in templates file {}'.format(
                args.template, args.templates_file)
        if args.verbose > 1 and templstr != None:
            print 'Template {} returned the argument string "{}"'.format(args.template, templstr)
    except IOError as e:
        if not args.quiet:
            print 'An error occurred while reading templates from {}'.format(args.aliases_file)
        if args.verbose > 0:
            print '\t', e
        

## additional sanity checking on arguments
if args.image_element == None or len(args.image_element) == 0:
    if not args.quiet:
        print "Error: No 'image' element was specified.\n"\
            "\tCannot grab comic. Aborting."
    sys.exit(1)

if args.next_element == None or len(args.next_element) == 0:
    if not args.quiet:
        print "Warning: No 'next' element was specified, can only grab the "\
            "given URL,\nno following pages\n"
    args.count = 1

if args.title_element == None or len(args.title_element) == 0:
    if args.verbose:
        print "Notice: No 'title' element was specified"


## print some info about what we're gonna do
if not args.quiet:
    if args.verbose > 1 and not libRequestsAvail:
        print "requests library is not available. Falling back to urllib2+httplib"
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
    if args.dry_run:
        print 'Dry run selected, image files will not be downloaded'    
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
