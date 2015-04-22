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
#street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
phonePattern = re.compile(r'(\d{3})\D*(\d{3})\D*(\d{4})\D*(\d*)$')

def is_phone(elem):
    return (elem.attrib['k'] == "phone")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    phone_num = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        i=1
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_phone(tag):
                    #print(tag.attrib['v'])
                    #audit_phone(phone_num, tag.attrib['v'])
                    phone_num[i].add(tag.attrib['v'])
                    i=+1
    return phone_num




def test():
    phone_num = audit(OSMFILE)

    pprint.pprint(dict(phone_num))

    for phone_num, ways in phone_num.iteritems():
        for num in ways:
            #newPhone=re.sub(phonePattern,phonePattern,name)
            newPhone=phone_format(num)
            print num, "=>", newPhone
            #print tag.attrib['k'], "=>", tag.attrib['v'] 


def phone_format(phone_number):
    #clean_phone_number = re.sub('[^0-9]+', '', phone_number)
    clean_phone_number = re.sub('[^0-9]+', '', phone_number)
    formatted_phone_number = re.sub("(\d)(?=(\d{3})+(?!\d))", r"\1 ", "%d" % int(clean_phone_number[:-1])) + clean_phone_number[-1]
    return formatted_phone_number

if __name__ == '__main__':
    test()
