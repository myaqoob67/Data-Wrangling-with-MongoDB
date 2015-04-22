#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json
#import audit
"""
Your task is to wrangle the data and transform the shape of the data
into the model we mentioned earlier. The output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

You have to complete the function 'shape_element'.
We have provided a function that will parse the map file, and call the function with the element
as an argument. You should return a dictionary, containing the shaped data for that element.
We have also provided a way to save the data in a file, so that you could use
mongoimport later on to import the shaped data into MongoDB. You could also do some cleaning
before doing that, like in the previous exercise, but for this exercise you just have to
shape the structure.

In particular the following things should be done:
- you should process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array are floats
      and not strings.
- if second level tag "k" value contains problematic characters, it should be ignored
- if second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if second level tag "k" value does not start with "addr:", but contains ":", you can process it
  same as any other tag.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]
"""

import audit2
import expphone

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
phonePattern = re.compile(r'(\d{3})\D*(\d{3})\D*(\d{4})\D*(\d*)$')
dash="-"

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "Rd.": "Road",
            "RD": "Road",
            "RD.": "Road",
            "Rd": "Road",
            "N.": "North",
            "N": "North",
            "S.": "South",
            "S": "South",
            "Blvd.": "Boulevard",
            "Blvd": "Boulevard",
            "E.": "East",
            "E": "East",
            "W.": "West",
            "W": "West",
            "Trl": "Trail",
            "Trl.": "Trail",
	    "Ave": "Avenue",
            "Ave.": "Avenue",
            "AVE": "Avenue",
            "AVE.": "Avenue"
            }


def shape_element(element):

    node = {}
    if element.tag == "node" or element.tag == "way":
        try:
            node['id'] = element.attrib['id']
        except:
            pass
        try:
            node['visible'] = element.attrib['visible']
        except:
            pass
        node['type'] = element.tag
        try:
            for way_ in element.iter('way'):
                for w in way_:
                    try:
                        if 'node_refs' in node:
                            node['node_refs'].append(w.attrib['ref'])
                        else:
                            node['node_refs'] = list()
                            node['node_refs'].append(w.attrib['ref'])
                    except:
                        continue
        except:
            pass

        try:
            node['pos'] = [float(element.attrib['lat']),float(element.attrib['lon'])]
        except:
            pass
        for item in CREATED:
            if item == CREATED[0]:
                node['created'] = {item:element.attrib[item]}
            else:
                node['created'].update({item:element.attrib[item]})
        for tag in element.iter('tag'):
            #print tag.attrib['k']
            if problemchars.search(tag.attrib['k']):
                pass
            elif tag.attrib['k'][:5] == 'addr:':
                #if audit2.is_street_name(tag):
                    #street_type = audit2.update_name(street_types, tag.attrib['v'])
                better_name = audit2.update_name(tag.attrib['v'], audit2.mapping)
                if 'address' not in node.keys() and ':' not in tag.attrib['k'].replace('addr:',''):
                    #node['address'] = {tag.attrib['k'].replace('addr:',''):tag.attrib['v']}
                    node['address'] = {tag.attrib['k'].replace('addr:',''):better_name}
                    #print tag.attrib['v'], "=>", better_name
                elif ':' not in tag.attrib['k'].replace('addr:',''):
                    #node['address'].update({tag.attrib['k'].replace('addr:',''):tag.attrib['v']})
                    node['address'].update({tag.attrib['k'].replace('addr:',''):better_name})
                    #print tag.attrib['v'], "=>", better_name
            else:
                #print tag.attrib['k']
                if tag.attrib['k'] == "phone":
                    newPhone=phonePattern.search(tag.attrib['v']).group()
                    newPhone=re.sub('\)','',newPhone)
                    newPhone=re.sub('-','',newPhone)
                    newPhone=re.sub(' ','',newPhone)
                    node[tag.attrib['k']]= newPhone
                    print tag.attrib['v'], "=>", newPhone
                """    
                elif tag.attrib['k'] == "addr:postcode":
                    print tag.attrib['k'], "=>",tag.attrib['v']
                    
                    if dash in tag.attrib['v']:
                        zip,ext=re.split('-', tag.attrib['v'])
                        node[tag.attrib['k']]=zip
                        print tag.attrib['v'], "=>", zip
                    else:
                        node[tag.attrib['k']]= tag.attrib['v']
                        #print tag.attrib['v'], "=>", tag.attrib['v']
                    """
                        
                #else:
                node[tag.attrib['k']]= tag.attrib['v']
                #print tag.attrib['k'], "=>", tag.attrib['v'] 
        #print node
        #pprint.pprint(node)
        return node
    
    else:
        return None



def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset,
    # call the process_map procedure with pretty=False. The pretty=True option adds
    # additional spaces to the output, making it significantly larger.
    process_map('c:/Temp/tucson.osm')


if __name__ == "__main__":
    test()
