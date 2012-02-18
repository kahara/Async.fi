#!/usr/bin/env python


import sys, os, datetime, json
from lxml import etree, objectify


source = etree.parse('./source/site.xml').getroot()


site = {
    'link': source.xpath('channel/link')[0].text,
    'title': source.xpath('channel/title')[0].text,
    'description': source.xpath('channel/description')[0].text,
    'posts': []
    }
for item in source.xpath('channel/item'):
    
    tags = []
    for tag in item.xpath('category[@domain="post_tag"]'):
        tags.append(tag.text)
    
    site['posts'].append({
            #'published': datetime.datetime.strptime(item.xpath('pubDate')[0].text, '%a, %d %b %Y %H:%M:%S +0000'),
            'published': item.xpath('pubDate')[0].text,
            'title': item.xpath('title')[0].text,
            'tags': tags,
            'category': item.xpath('category[@domain="category"]')[0].text,
            #'body': item.xpath('content:encoded', namespaces={'content': 'http://purl.org/rss/1.0/modules/content/'})[0].text
        })
print json.dumps(site, indent=4)
