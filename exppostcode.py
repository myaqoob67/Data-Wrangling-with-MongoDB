"""
Your task in this exercise has two steps:

- audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix 
    the unexpected street types to the appropriate ones in the expected list.
    You have to add mappings only for the actual problems you find in this OSMFILE,
    not a generalized solution, since that may and will depend on the particular area you are auditing.
- write the update_name function, to actually fix the street name.
    The function takes a string with street name as an argument and should return the fixed name
    We have provided a simple test so that you see what exactly is expected
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "c:/Temp/tucson.osm"
dash = "-"

def is_postcode(elem):
    return (elem.attrib['k'] == "addr:postcode")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    postcode_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        i=1
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postcode(tag):
                    #print(tag.attrib['v'])
                    postcode_types[i].add(tag.attrib['v'])
                    i=+1

    return postcode_types

def postcode_format(postcode):
    if dash in postcode:
        zip,ext=re.split('-', postcode)
        return zip
        
    else:
        return postcode

def test():
    post_types = audit(OSMFILE)

    pprint.pprint(dict(post_types))

    for post_type, ways in post_types.iteritems():
        for pcode in ways:
            newPostcode=postcode_format(pcode)
            print pcode,"=>",newPostcode 


if __name__ == '__main__':
    test()
