#!/usr/bin/python
# Extracts plain text from articles converted into "XML" using wiki2xml_all.
#
# Evan Jones <evanj@mit.edu>
# April, 2008
# Released under a BSD licence.
# http://evanjones.ca/software/wikipedia2text.html

import os
import sys

import wikisoup

def findXMLIterator(path):
    """Iterates over all .xml files in path."""
    for file in os.listdir(path):
        fullpath = os.path.join(path, file)
        if os.path.isdir(fullpath):
            for i in findXMLIterator(fullpath):
                yield i
        elif fullpath.endswith(".xml"):
            yield fullpath

output = open(sys.argv[2], "w")

# Extract the words from all the files in the subdirectories
for xmlfile in findXMLIterator(sys.argv[1]):
    try:
        output.write(wikisoup.extractWikipediaText(xmlfile).encode("UTF-8"))
    except:
        print xmlfile
        raise
